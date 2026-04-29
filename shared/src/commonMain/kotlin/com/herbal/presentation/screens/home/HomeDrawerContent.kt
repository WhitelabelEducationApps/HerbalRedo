package com.herbal.presentation.screens.home

import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Icon
import androidx.compose.material3.NavigationDrawerItem
import androidx.compose.material3.Switch
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
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
    val availableViewModes = appConfig.getAvailableViewModes()
    val showViewModeSwitcher = availableViewModes.size > 1

    // Get strings from resources
    val gridViewLabel = context.getString(context.resources.getIdentifier("grid_view", "string", context.packageName))
    val mapViewLabel = context.getString(context.resources.getIdentifier("map_view", "string", context.packageName))
    val languageLabel = context.getString(context.resources.getIdentifier("language", "string", context.packageName))
    val viewOptionsLabel = context.getString(context.resources.getIdentifier("view_options", "string", context.packageName))
    val useLocationPlantsLabel = context.getString(context.resources.getIdentifier("use_location_plants", "string", context.packageName))

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
