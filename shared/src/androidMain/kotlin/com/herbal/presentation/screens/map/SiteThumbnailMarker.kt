package com.herbal.presentation.screens.map

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Card
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.unit.dp
import coil3.compose.AsyncImage
import coil3.compose.LocalPlatformContext
import coil3.request.ImageRequest
import coil3.request.allowHardware
import com.herbal.data.models.HeritageSite
import com.herbal.utils.getDrawableResourceId
import com.herbal.utils.toDrawableResourceName

@Composable
fun SiteThumbnailMarker(site: HeritageSite) {
    val context = LocalPlatformContext.current
    val resourceName = site.name.toDrawableResourceName()
    val drawableId = getDrawableResourceId(resourceName)
    val imageUrl = site.imageUrl?.split(",")?.firstOrNull()?.trim()
    val imageModel = if (drawableId != 0) drawableId else imageUrl

    Card(
        modifier = Modifier
            .size(60.dp)
            .shadow(4.dp, RoundedCornerShape(8.dp)),
        shape = RoundedCornerShape(8.dp),
        border = BorderStroke(2.dp, Color.White)
    ) {
        AsyncImage(
            model = ImageRequest.Builder(context)
                .data(imageModel)
                .allowHardware(false) // Fix hardware bitmap error
                .build(),
            contentDescription = site.getLocalizedName(),
            modifier = Modifier.fillMaxSize(),
            contentScale = ContentScale.Crop
        )
    }
}