package com.herbal.presentation.screens.home

import androidx.compose.runtime.Composable
import com.whitelabel.platform.utils.ExtractedColors

@Composable
expect fun rememberExtractedColors(siteId: Long, drawableResourceId: Int?): ExtractedColors?
