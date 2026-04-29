package com.herbal.presentation.screens.home

import android.Manifest
import android.content.pm.PackageManager
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.DrawerValue
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.ModalNavigationDrawer
import androidx.compose.material3.Scaffold
import androidx.compose.material3.SnackbarHost
import androidx.compose.material3.SnackbarHostState
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.rememberDrawerState
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.core.content.ContextCompat
import com.herbal.utils.LocationFilterPreferences
import com.herbal.utils.OnboardingPreferences
import com.herbal.utils.ZoneGeoMapper
import com.herbal.utils.getLocationLastKnown
import com.herbal.utils.getStringResource
import com.whitelabel.core.AppConfig
import com.whitelabel.core.presentation.home.ViewMode
import com.whitelabel.platform.utils.debugLogD
import com.whitelabel.platform.utils.logLifecycle
import com.whitelabel.platform.utils.logStateChange
import com.whitelabel.platform.utils.logUserAction
import kotlinx.coroutines.launch
import org.koin.compose.koinInject

private const val TAG = "HomeScreen"

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun HomeScreen(
    viewModel: HomeViewModel,
    onSiteClick: (Long) -> Unit,
    onNavigateToLanguage: () -> Unit,
    snackbarHostState: SnackbarHostState = remember { SnackbarHostState() },
    modifier: Modifier = Modifier
) {
    logLifecycle(TAG, "Composable entered")

    val context = LocalContext.current
    val uiState by viewModel.uiState.collectAsState()
    val searchQuery by viewModel.searchQuery.collectAsState()
    val viewMode by viewModel.viewMode.collectAsState()
    val focusedSiteId by viewModel.focusedItemId.collectAsState()
    val appConfig: AppConfig = koinInject()
    val drawerState = rememberDrawerState(DrawerValue.Closed)
    val scope = rememberCoroutineScope()
    var searchActive by rememberSaveable { mutableStateOf(false) }

    // Location filter state
    val useLocationFilter by LocationFilterPreferences.useLocationFilter.collectAsState()

    // Onboarding dialog state
    val onboardingShown by OnboardingPreferences.onboardingShown.collectAsState()
    var showOnboardingDialog by remember { mutableStateOf(false) }

    // Show onboarding dialog on first launch
    LaunchedEffect(onboardingShown) {
        if (!onboardingShown) {
            showOnboardingDialog = true
        }
    }

    // Permission launcher for location
    val permissionLauncher = rememberLauncherForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { granted ->
        if (granted) {
            scope.launch {
                val location = getLocationLastKnown(context)
                if (location != null) {
                    val zone = ZoneGeoMapper.getZoneForLocation(location.first, location.second)
                    LocationFilterPreferences.setCurrentUserZone(zone)
                    LocationFilterPreferences.setUseLocationFilter(true)
                    debugLogD(TAG, "Location granted, zone=$zone")
                } else {
                    LocationFilterPreferences.setUseLocationFilter(true)
                    debugLogD(TAG, "Location granted but no fix yet, filter on without zone")
                }
            }
        } else {
            LocationFilterPreferences.setUseLocationFilter(false)
            scope.launch {
                snackbarHostState.showSnackbar(
                    getStringResource("location_permission_denied")
                )
            }
            debugLogD(TAG, "Location permission denied, toggle reverted")
        }
    }

    // Log state changes
    DisposableEffect(uiState) {
        debugLogD(TAG, "uiState updated: ${uiState.javaClass.simpleName}")
        onDispose { }
    }

    DisposableEffect(viewMode) {
        logStateChange(TAG, "viewMode", null, viewMode)
        onDispose { }
    }

    DisposableEffect(searchQuery) {
        if (searchQuery.isNotEmpty()) {
            debugLogD(TAG, "searchQuery: '$searchQuery'")
        }
        onDispose { }
    }

    DisposableEffect(focusedSiteId) {
        if (focusedSiteId != null) {
            debugLogD(TAG, "focusedSiteId: $focusedSiteId")
        }
        onDispose { }
    }

    // First-launch onboarding dialog
    if (showOnboardingDialog) {
        AlertDialog(
            onDismissRequest = {
                showOnboardingDialog = false
                OnboardingPreferences.markShown()
            },
            title = { Text(getStringResource("onboarding_title")) },
            text = { Text(getStringResource("onboarding_message")) },
            confirmButton = {
                TextButton(onClick = {
                    showOnboardingDialog = false
                    OnboardingPreferences.markShown()
                }) {
                    Text(getStringResource("onboarding_ok"))
                }
            }
        )
    }

    ModalNavigationDrawer(
        drawerState = drawerState,
        gesturesEnabled = viewMode != ViewMode.Map,
        drawerContent = {
            logLifecycle(TAG, "Drawer content composed")
            HomeDrawerContent(
                viewMode = viewMode,
                onViewModeChange = { newMode ->
                    logUserAction(TAG, "switched view mode", "from $viewMode to $newMode")
                    viewModel.setViewMode(newMode)
                },
                onLanguageClick = {
                    logUserAction(TAG, "opened language selection")
                    onNavigateToLanguage()
                },
                appConfig = appConfig,
                onCloseDrawer = { scope.launch { drawerState.close() } },
                useLocationFilter = useLocationFilter,
                onLocationFilterToggle = { newValue ->
                    logUserAction(TAG, "toggled location filter", "newValue=$newValue")
                    if (newValue) {
                        // Turning ON: check/request permission first
                        val hasPermission = ContextCompat.checkSelfPermission(
                            context, Manifest.permission.ACCESS_FINE_LOCATION
                        ) == PackageManager.PERMISSION_GRANTED
                        if (hasPermission) {
                            scope.launch {
                                val location = getLocationLastKnown(context)
                                val zone = location?.let {
                                    ZoneGeoMapper.getZoneForLocation(it.first, it.second)
                                }
                                LocationFilterPreferences.setCurrentUserZone(zone)
                                LocationFilterPreferences.setUseLocationFilter(true)
                                debugLogD(TAG, "Location already granted, zone=$zone")
                            }
                        } else {
                            permissionLauncher.launch(Manifest.permission.ACCESS_FINE_LOCATION)
                        }
                    } else {
                        LocationFilterPreferences.setUseLocationFilter(false)
                    }
                }
            )
        }
    ) {
        Scaffold(
            topBar = {
                HomeTopAppBar(
                    searchActive = searchActive,
                    searchQuery = searchQuery,
                    onSearchQueryChange = { query ->
                        if (query != searchQuery) {
                            debugLogD(TAG, "search query changed: '$query'")
                        }
                        viewModel.onSearchQueryChange(query)
                    },
                    onSearchActiveChange = { active ->
                        logStateChange(TAG, "searchActive", searchActive, active)
                        searchActive = active
                    },
                    onOpenDrawer = {
                        logUserAction(TAG, "opened navigation drawer")
                        scope.launch { drawerState.open() }
                    }
                )
            },
            snackbarHost = {
                SnackbarHost(hostState = snackbarHostState)
            }
        ) { paddingValues ->
            Column(
                modifier = modifier.fillMaxSize().padding(paddingValues)
            ) {
                HomeContent(
                    uiState = uiState,
                    viewMode = viewMode,
                    searchQuery = searchQuery,
                    focusedSiteId = focusedSiteId,
                    onSiteClick = { siteId ->
                        logUserAction(TAG, "clicked site", "siteId=$siteId")
                        onSiteClick(siteId)
                    },
                    onFavoriteClick = { site ->
                        logUserAction(TAG, "toggled favorite", "siteId=${site.id}, name=${site.name}")
                        viewModel.onFavoriteClick(site)
                    },
                    onClearFocusedSite = {
                        debugLogD(TAG, "clearing focused site")
                        viewModel.clearFocusedItem()
                    },
                    showCategory = appConfig.enableCategories
                )
            }
        }
    }
}
