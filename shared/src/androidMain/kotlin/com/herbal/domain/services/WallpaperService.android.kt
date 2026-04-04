package com.herbal.domain.services

import android.annotation.SuppressLint
import android.app.WallpaperManager
import android.content.Context
import android.graphics.BitmapFactory
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.net.URL

class AndroidWallpaperService(private val context: Context) : WallpaperService {
    @SuppressLint("MissingPermission")
    override suspend fun setWallpaper(imageUrl: String): Result<Unit> = withContext(Dispatchers.IO) {
        try {
            val wallpaperManager = WallpaperManager.getInstance(context)
            val connection = URL(imageUrl).openConnection()
            val inputStream = connection.getInputStream()
            val bitmap = BitmapFactory.decodeStream(inputStream)
            inputStream.close()

            wallpaperManager.setBitmap(bitmap, null, true,
                WallpaperManager.FLAG_SYSTEM or WallpaperManager.FLAG_LOCK)

            Result.success(Unit)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
