package com.herbal.presentation.components

// Re-export from core
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.TextStyle
import androidx.compose.material3.LocalTextStyle

@Composable
fun MarqueeText(
    text: String,
    modifier: Modifier = Modifier,
    style: TextStyle = LocalTextStyle.current,
    color: Color = Color.Unspecified,
    delayMillis: Long = 2000,
    velocityDpPerSecond: Float = 30f
) = com.whitelabel.core.presentation.components.MarqueeText(
    text = text,
    modifier = modifier,
    style = style,
    color = color,
    delayMillis = delayMillis,
    velocityDpPerSecond = velocityDpPerSecond
)
