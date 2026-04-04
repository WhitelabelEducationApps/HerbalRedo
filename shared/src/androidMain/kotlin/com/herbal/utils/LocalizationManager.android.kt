package com.herbal.utils

import android.content.res.Resources
import java.util.Locale

actual object LocalizationManager {
    actual fun getCurrentLanguageCode(): String {
        return Locale.getDefault().language
    }
}
