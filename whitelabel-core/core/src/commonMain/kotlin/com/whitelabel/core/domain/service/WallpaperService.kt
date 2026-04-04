package com.whitelabel.core.domain.service

/**
 * Platform-specific wallpaper service. Android implements with WallpaperManager,
 * other platforms provide no-op or platform-appropriate implementations.
 */
interface WallpaperService {
    suspend fun setWallpaper(imageUrl: String): kotlin.Result<Unit>
}
