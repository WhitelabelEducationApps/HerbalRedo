package com.herbal.presentation.screens.home

import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Icon
import androidx.compose.material3.NavigationDrawerItem
import androidx.compose.material3.Switch
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import com.herbal.utils.LanguagePreferences
import com.whitelabel.core.AppConfig
import com.whitelabel.core.presentation.home.ViewMode
import com.whitelabel.core.presentation.home.getAvailableViewModes
import com.whitelabel.platform.presentation.screens.home.CatalogNavigationDrawer
import com.whitelabel.platform.presentation.screens.home.DrawerMenuItem
import com.whitelabel.platform.utils.debugLogD
import com.whitelabel.platform.utils.logLifecycle
import com.whitelabel.platform.utils.logUserAction
import herbalredo.shared.generated.resources.Res
import herbalredo.shared.generated.resources.grid_view
import herbalredo.shared.generated.resources.language
import herbalredo.shared.generated.resources.location_on
import herbalredo.shared.generated.resources.map
import org.jetbrains.compose.resources.DrawableResource
import org.jetbrains.compose.resources.ExperimentalResourceApi
import org.jetbrains.compose.resources.painterResource
import java.util.Locale

private const val TAG = "HomeDrawerContent"

@OptIn(ExperimentalResourceApi::class)
@Composable
fun HomeDrawerContent(
    viewMode: ViewMode,
    onViewModeChange: (ViewMode) -> Unit,
    onLanguageClick: () -> Unit,
    onCloseDrawer: () -> Unit,
    appConfig: AppConfig,
    useLocationFilter: Boolean = false,
    onLocationFilterToggle: (Boolean) -> Unit = {},
    modifier: Modifier = Modifier
) {
    logLifecycle(TAG, "Composable entered, currentViewMode=$viewMode")
    val context = LocalContext.current
    val selectedLanguage by LanguagePreferences.selectedLanguage.collectAsState()
    val availableViewModes = appConfig.getAvailableViewModes()
    val showViewModeSwitcher = availableViewModes.size > 1

    // Build a locale-aware context so strings reflect the selected language
    // even before the Activity recreates (e.g. when drawer is open during switch).
    val localizedContext = remember(selectedLanguage) {
        val locale = selectedLanguage?.let { Locale(it.code) } ?: Locale.getDefault()
        val config = android.content.res.Configuration(context.resources.configuration)
        config.setLocale(locale)
        context.createConfigurationContext(config)
    }

    // Get strings from resources
    fun str(name: String) = localizedContext.getString(
        localizedContext.resources.getIdentifier(name, "string", context.packageName)
    )
    val gridViewLabel = str("grid_view")
    val mapViewLabel = str("map_view")
    val languageLabel = str("language")
    val viewOptionsLabel = str("view_options")
    val useLocationPlantsLabel = str("use_location_plants")

    val menuItems = mutableListOf<DrawerMenuItem>()

    // Only show view mode options if multiple modes are available
    if (showViewModeSwitcher) {
        menuItems.add(DrawerMenuItem(
            label = gridViewLabel,
            icon = Res.drawable.grid_view,
            viewMode = ViewMode.Grid
        ))

        if (appConfig.enableMap) {
            menuItems.add(DrawerMenuItem(
                label = mapViewLabel,
                icon = Res.drawable.map,
                viewMode = ViewMode.Map
            ))
        }
    }

    // Always show language option
    menuItems.add(DrawerMenuItem(
        label = languageLabel,
        icon = Res.drawable.language,
        isAction = true,
        onClick = onLanguageClick
    ))

    // Location filter toggle
    menuItems.add(DrawerMenuItem(
        label = useLocationPlantsLabel,
        icon = Res.drawable.location_on,
        isAction = true,
        isToggle = true,
        toggleChecked = useLocationFilter,
        onClick = { onLocationFilterToggle(!useLocationFilter) }
    ))

    CatalogNavigationDrawer(
        currentViewMode = viewMode,
        onViewModeChange = { newMode ->
            logUserAction(TAG, "selected view mode", "newMode=$newMode")
            onViewModeChange(newMode)
        },
        menuItems = menuItems,
        headerTitle = viewOptionsLabel,
        onCloseDrawer = {
            debugLogD(TAG, "Closing drawer")
            onCloseDrawer()
        },
        modifier = modifier,
        itemContent = { item, isSelected, onClick ->
            debugLogD(TAG, "Rendering drawer item: ${item.label}, selected=$isSelected, isToggle=${item.isToggle}")
            val iconRes = item.icon as? DrawableResource
            NavigationDrawerItem(
                label = { Text(item.label) },
                icon = iconRes?.let { res ->
                    { Icon(painterResource(res), contentDescription = item.label) }
                },
                selected = isSelected,
                badge = if (item.isToggle) {
                    {
                        Switch(
                            checked = item.toggleChecked,
                            onCheckedChange = {
                                logUserAction(TAG, "toggled drawer item", item.label)
                                onClick()
                            }
                        )
                    }
                } else null,
                onClick = {
                    logUserAction(TAG, "clicked drawer item", item.label)
                    onClick()
                },
                modifier = Modifier.padding(horizontal = 12.dp, vertical = 4.dp)
            )
        }
    )
}
