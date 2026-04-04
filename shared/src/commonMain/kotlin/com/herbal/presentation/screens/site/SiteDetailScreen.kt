package com.herbal.presentation.screens.site

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.LocationOn
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.runtime.DisposableEffect
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.unit.dp
import coil3.compose.AsyncImage
import coil3.compose.LocalPlatformContext
import coil3.request.ImageRequest
import com.herbal.data.models.HeritageSite
import com.herbal.utils.LOG
import com.herbal.utils.getDrawableResourceId
import com.herbal.utils.getPrimaryColor
import com.herbal.utils.toDrawableResourceName
import com.whitelabel.core.AppConfig
import com.whitelabel.platform.presentation.screens.detail.GenericDetailScreen
import com.whitelabel.platform.utils.debugLogD
import com.whitelabel.platform.utils.logLifecycle
import com.whitelabel.platform.utils.logUserAction
import herbalredo.shared.generated.resources.Res
import herbalredo.shared.generated.resources.fullscreen
import herbalredo.shared.generated.resources.map
import org.jetbrains.compose.resources.ExperimentalResourceApi
import org.jetbrains.compose.resources.painterResource

private const val TAG = "SiteDetailScreen"

@OptIn(ExperimentalResourceApi::class)
@Composable
fun SiteDetailScreen(
    viewModel: SiteDetailViewModel,
    onBackClick: () -> Unit,
    onShowFullImage: (Long) -> Unit,
    onShowOnMap: (Long) -> Unit,
    appConfig: AppConfig
) {
    logLifecycle(TAG, "Composable entered")
    
    DisposableEffect(Unit) {
        debugLogD(TAG, "SiteDetailScreen mounted")
        onDispose {
            debugLogD(TAG, "SiteDetailScreen unmounted")
        }
    }

    GenericDetailScreen(
        viewModel = viewModel,
        onBackClick = {
            logUserAction(TAG, "clicked back")
            onBackClick()
        },
        languageCode = "en",
        topBarColor = Color(0xFF1976D2),
        topBarContentColor = Color.White,
        floatingActionButton = { site ->
            logLifecycle(TAG, "Rendering FAB for site ${site.id}")
            Column(
                modifier = Modifier.padding(16.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp),
                horizontalAlignment = Alignment.End
            ) {
                if (site.latitude != null && site.longitude != null && appConfig.enableMap) {
                    debugLogD(TAG, "Showing map FAB (lat=${site.latitude}, lng=${site.longitude})")
                    SmallFloatingActionButton(
                        onClick = {
                            logUserAction(TAG, "clicked show on map", "siteId=${site.id}")
                            onShowOnMap(site.id)
                        }
                    ) {
                        Icon(
                            painter = painterResource(Res.drawable.map),
                            contentDescription = "Show on Map"
                        )
                    }
                }
                FloatingActionButton(
                    onClick = {
                        logUserAction(TAG, "clicked view fullscreen", "siteId=${site.id}")
                        onShowFullImage(site.id)
                    }
                ) {
                    val fullscreenPainter = painterResource(Res.drawable.fullscreen)
                    Icon(
                        painter = fullscreenPainter,
                        contentDescription = "View Fullscreen"
                    )
                }
            }
        },
        content = { site, localizedGroupName, paddingValues ->
            debugLogD(TAG, "Rendering content for site ${site.id}, group=$localizedGroupName")
            SiteDetailContent(
                site = site,
                localizedCountries = localizedGroupName ?: "",
                modifier = Modifier.padding(paddingValues)
            )
        }
    )
}

@Composable
private fun SiteDetailContent(
    site: HeritageSite,
    localizedCountries: String,
    modifier: Modifier = Modifier
) {
    Column(
        modifier = modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(16.dp)
    ) {
        val context = LocalPlatformContext.current
        val resourceName = site.name.toDrawableResourceName()
        val drawableId = getDrawableResourceId(resourceName)
        val imageUrl = site.imageUrl?.split(",")?.firstOrNull()?.trim()
        val imageModel = if (drawableId != 0) drawableId else imageUrl
        if (drawableId == 0) {
            LOG("ERROR WE COULD NOT FIND DRAWABLE ID FOR $resourceName  from ${site.name}")
        }

        if (imageModel != null) {
            AsyncImage(
                model = ImageRequest.Builder(context).data(imageModel).build(),
                contentDescription = site.getLocalizedName(),
                modifier = Modifier
                    .fillMaxWidth()
                    .height(200.dp)
                    .clip(RoundedCornerShape(8.dp)),
                contentScale = ContentScale.Crop
            )
            Spacer(modifier = Modifier.height(16.dp))
        }

        site.location?.let {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(
                    Icons.Default.LocationOn,
                    contentDescription = null,
                    modifier = Modifier.size(20.dp),
                    tint = MaterialTheme.colorScheme.primary
                )
                Spacer(Modifier.width(8.dp))
                Text(
                    text = it,
                    style = MaterialTheme.typography.bodyLarge,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
            Spacer(modifier = Modifier.height(8.dp))
        }

        if (localizedCountries.isNotBlank()) {
            Text(
                text = localizedCountries,
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
            Spacer(modifier = Modifier.height(8.dp))
        }

        Spacer(modifier = Modifier.height(8.dp))
        HorizontalDivider()
        Spacer(modifier = Modifier.height(16.dp))

        site.getLocalizedDescription()?.let { description ->
            if (description.isNotBlank()) {
                Text(
                    text = description,
                    style = MaterialTheme.typography.bodyLarge,
                    color = MaterialTheme.colorScheme.onSurface
                )
            }
        } ?: Text(
            text = "No description available",
            style = MaterialTheme.typography.bodyLarge,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
    }
}
