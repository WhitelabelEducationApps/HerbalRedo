plugins {
    alias(libs.plugins.kotlinMultiplatform)
    alias(libs.plugins.androidLibrary)
    alias(libs.plugins.sqldelight)
    alias(libs.plugins.jetbrainsCompose)
    alias(libs.plugins.composeCompiler)
}

compose.resources {
    publicResClass = false
    packageOfResClass = "herbalredo.shared.generated.resources"
    generateResClass = always
}

kotlin {
    androidTarget {
        compilerOptions {
            jvmTarget.set(org.jetbrains.kotlin.gradle.dsl.JvmTarget.JVM_17)
        }
    }

    listOf(
        iosX64(),
        iosArm64(),
        iosSimulatorArm64()
    ).forEach {
        it.binaries.framework {
            baseName = "shared"
            isStatic = true
        }
    }

    sourceSets {
        val commonMain by getting {
            dependencies {
                api("com.whitelabel:core:0.1.0")
                api("com.whitelabel:platform:0.1.0")
                implementation(compose.runtime)
                implementation(compose.foundation)
                implementation(compose.material3)
                implementation(compose.ui)
                implementation(compose.components.resources)
                implementation(compose.materialIconsExtended)
                implementation(libs.kotlinx.coroutines.core)
                implementation(libs.sqldelight.coroutines)
                implementation(libs.kermit)
                implementation(libs.coil.compose)
                implementation(libs.coil.network.ktor)
                implementation(libs.ktor.client.core)
                implementation(libs.koin.core)
            }
        }

        val commonTest by getting {
            dependencies {
                implementation(kotlin("test"))
                implementation(libs.kotlinx.coroutines.test)
                implementation(libs.turbine)
            }
        }

        val androidUnitTest by getting {
            dependencies {
                implementation(libs.mockk)
            }
        }

        val androidMain by getting {
            dependencies {
                // SQLDelight driver for this app's database
                implementation(libs.sqldelight.driver.android)
                // Maps for this app's map view
                implementation(libs.maps.compose)
                implementation(libs.play.services.maps)
                implementation(libs.maps.compose.utils)
                // Ktor HTTP client
                implementation(libs.ktor.client.okhttp)
                implementation(libs.ktor.client.logging)
                // Koin for Android
                implementation(libs.koin.android)
                implementation(libs.koin.compose)
                // Palette API for color extraction
                implementation("androidx.palette:palette:1.0.0")
                // DataStore for preferences
                implementation(libs.androidx.datastore)
                // Location services for GPS-based plant filtering
                implementation(libs.play.services.location)
                // Activity result API for permission launcher
                implementation(libs.androidx.activity.compose)
            }
        }

        val iosMain by creating {
            dependsOn(commonMain)
            dependencies {
                implementation(libs.sqldelight.driver.native)
            }
        }

        val iosX64Main by getting { dependsOn(iosMain) }
        val iosArm64Main by getting { dependsOn(iosMain) }
        val iosSimulatorArm64Main by getting { dependsOn(iosMain) }
    }
}

android {
    namespace = "com.herbal.shared"
    compileSdk = 35

    defaultConfig {
        minSdk = 23
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    packaging {
        jniLibs {
            useLegacyPackaging = false
        }
    }
}

sqldelight {
    databases {
        create("HerbalDatabase") {
            packageName.set("com.herbal.data.local")
            schemaOutputDirectory.set(file("src/commonMain/sqldelight/com/herbal/data/local"))
            version=2
        }
    }
}
