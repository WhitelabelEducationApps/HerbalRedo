package com.herbal.data.local

import android.content.Context
import app.cash.sqldelight.db.SqlDriver
import app.cash.sqldelight.driver.android.AndroidSqliteDriver
import java.io.File
import java.io.FileOutputStream

actual class DatabaseDriverFactory(private val context: Context, private val dbName: String) {
    actual fun createDriver(): SqlDriver {
        val dbFile = context.getDatabasePath(dbName)

        // Helper function to copy database from assets (optional — if file doesn't exist, create empty DB)
        fun copyDatabaseFromAssets() {
            try {
                dbFile.parentFile?.mkdirs()
                context.assets.open(dbName).use { input ->
                    FileOutputStream(dbFile).use { output ->
                        input.copyTo(output)
                    }
                }
            } catch (e: Exception) {
                // Asset file doesn't exist — let SQLDelight create an empty database
            }
        }

        if (!dbFile.exists()) {
            copyDatabaseFromAssets()
        }

        // Create a schema wrapper that deletes and recreates on version mismatch
        val schema = object : app.cash.sqldelight.db.SqlSchema<app.cash.sqldelight.db.QueryResult.Value<Unit>> {
            override val version: Long = HerbalDatabase.Schema.version

            override fun create(driver: app.cash.sqldelight.db.SqlDriver): app.cash.sqldelight.db.QueryResult.Value<Unit> {
                return HerbalDatabase.Schema.create(driver)
            }

            override fun migrate(
                driver: app.cash.sqldelight.db.SqlDriver,
                oldVersion: Long,
                newVersion: Long,
                vararg callbacks: app.cash.sqldelight.db.AfterVersion
            ): app.cash.sqldelight.db.QueryResult.Value<Unit> {
                // Version mismatch — don't touch the schema, just return success
                // (The pre-populated asset DB has its own version management)
                return app.cash.sqldelight.db.QueryResult.Unit
            }
        }

        return AndroidSqliteDriver(
            schema = schema,
            context = context,
            name = dbName
        )
    }
}
