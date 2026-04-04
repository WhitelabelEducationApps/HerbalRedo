package com.herbal.presentation.screens.home

import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Icon
import androidx.compose.material3.NavigationDrawerItem
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.whitelabel.core.AppConfig
import com.whitelabel.core.presentation.home.ViewMode
import com.whitelabel.platform.presentation.screens.home.CatalogNavigationDrawer
import com.whitelabel.platform.presentation.screens.home.DrawerMenuItem
import com.whitelabel.platform.utils.debugLogD
import com.whitelabel.platform.utils.logLifecycle
import com.whitelabel.platform.utils.logUserAction
import herbalredo.shared.generated.resources.Res
import herbalredo.shared.generated.resources.grid_view
import herbalredo.shared.generated.resources.language
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
    modifier: Modifier = Modifier
) {
    logLifecycle(TAG, "Composable entered, currentViewMode=$viewMode")
    val menuItems = mutableListOf(
        DrawerMenuItem(
            label = "Grid View",
            icon = Res.drawable.grid_view,
            viewMode = ViewMode.Grid
        ),
        DrawerMenuItem(
            label = "Language",
            icon = Res.drawable.language,
            isAction = true,
            onClick = onLanguageClick
        )
    )

    if (appConfig.enableMap) {
        menuItems.add(1, DrawerMenuItem(
            label = "Map View",
            icon = Res.drawable.map,
            viewMode = ViewMode.Map
        ))
    }

    CatalogNavigationDrawer(
        currentViewMode = viewMode,
        onViewModeChange = { newMode ->
            logUserAction(TAG, "selected view mode", "newMode=$newMode")
            onViewModeChange(newMode)
        },
        menuItems = menuItems,
        headerTitle = "View Options",
        onCloseDrawer = {
            debugLogD(TAG, "Closing drawer")
            onCloseDrawer()
        },
        modifier = modifier,
        itemContent = { item, isSelected, onClick ->
            debugLogD(TAG, "Rendering drawer item: ${item.label}, selected=$isSelected")
            val iconRes = item.icon as? DrawableResource
            NavigationDrawerItem(
                label = { Text(item.label) },
                icon = iconRes?.let { res ->
                    { Icon(painterResource(res), contentDescription = item.label) }
                },
                selected = isSelected,
                onClick = {
                    logUserAction(TAG, "clicked drawer item", item.label)
                    onClick()
                },
                modifier = Modifier.padding(horizontal = 12.dp, vertical = 4.dp)
            )
        }
    )
}
