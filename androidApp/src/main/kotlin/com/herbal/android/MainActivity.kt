package com.herbal.android

import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import com.herbal.presentation.theme.HerbalTheme
import com.whitelabel.platform.WhitelabelActivity

class MainActivity : WhitelabelActivity() {
    @Composable
    override fun createContent() {
        HerbalTheme {
            Surface(
                modifier = Modifier.fillMaxSize(),
                color = MaterialTheme.colorScheme.background
            ) {
                AppNavigation()
            }
        }
    }
}
