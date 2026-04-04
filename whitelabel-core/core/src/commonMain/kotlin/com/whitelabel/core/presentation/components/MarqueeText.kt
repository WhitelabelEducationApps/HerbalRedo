package com.whitelabel.core.presentation.components

import androidx.compose.animation.core.*
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.material3.LocalTextStyle
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clipToBounds
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.onGloballyPositioned
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.unit.dp
import kotlinx.coroutines.delay

@Composable
fun MarqueeText(
    text: String,
    modifier: Modifier = Modifier,
    style: TextStyle = LocalTextStyle.current,
    color: Color = Color.Unspecified,
    delayMillis: Long = 2000,
    velocityDpPerSecond: Float = 30f
) {
    var textWidth by remember { mutableStateOf(0) }
    var containerWidth by remember { mutableStateOf(0) }
    val scrollState = rememberScrollState()

    val needsScrolling = textWidth > containerWidth && containerWidth > 0

    LaunchedEffect(needsScrolling, textWidth, containerWidth) {
        if (!needsScrolling) return@LaunchedEffect

        while (true) {
            delay(delayMillis)

            val distance = (textWidth - containerWidth).toFloat()
            val duration = ((distance / velocityDpPerSecond) * 1000).toInt()

            scrollState.animateScrollTo(
                value = textWidth - containerWidth,
                animationSpec = tween(durationMillis = duration, easing = LinearEasing)
            )

            delay(delayMillis)

            scrollState.animateScrollTo(
                value = 0,
                animationSpec = tween(durationMillis = duration, easing = LinearEasing)
            )
        }
    }

    Box(
        modifier = modifier
            .clipToBounds()
            .onGloballyPositioned { coordinates ->
                containerWidth = coordinates.size.width
            }
    ) {
        Box(
            modifier = Modifier.horizontalScroll(scrollState, enabled = false)
        ) {
            Text(
                text = text,
                style = style,
                color = color,
                maxLines = 1,
                softWrap = false,
                modifier = Modifier
                    .padding(end = if (needsScrolling) 32.dp else 0.dp)
                    .onGloballyPositioned { coordinates ->
                        textWidth = coordinates.size.width
                    }
            )
        }
    }
}
