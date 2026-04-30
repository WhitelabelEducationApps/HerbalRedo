import java.util.Properties
import java.io.FileInputStream

plugins {
    alias(libs.plugins.androidApplication)
    alias(libs.plugins.kotlinAndroid)
    alias(libs.plugins.composeCompiler)
}

android {
    namespace = "com.herbal.android"
    compileSdk = 35

    signingConfigs {
        create("release") {
            storeFile = file("../uploadKey.jks")
            storePassword = "electronica09"
            keyAlias = "radu"
            keyPassword = "electronica09"
        }
    }

    defaultConfig {
        applicationId = "com.beacon.medicinalplantsnew"
        minSdk = 23
        targetSdk = 35
        versionCode = 71
        versionName = "1.1.5"

        val properties = Properties()
        val localPropertiesFile = rootProject.file("local.properties")
        if (localPropertiesFile.exists()) {
            properties.load(FileInputStream(localPropertiesFile))
        }

        // BuildConfig field for API key
        val mapsApiKey = properties.getProperty("maps.apiKey") ?: ""
        buildConfigField("String", "MAPS_API_KEY", "\"$mapsApiKey\"")

        // Resources for manifest placeholder
        resValue("string", "maps_api_key", mapsApiKey)
    }

    buildTypes {
        release {
            signingConfig = signingConfigs.getByName("release")
        }
    }

    buildFeatures {
        compose = true
        buildConfig = true
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

kotlin {
    compilerOptions {
        jvmTarget.set(org.jetbrains.kotlin.gradle.dsl.JvmTarget.JVM_17)
    }
}

dependencies {
    implementation(project(":shared"))
    implementation(platform("androidx.compose:compose-bom:2024.02.00"))
    implementation("androidx.compose.ui:ui")
    implementation("androidx.compose.material3:material3")
    implementation(libs.androidx.activity.compose)
    implementation(libs.androidx.navigation.compose)
    implementation(libs.androidx.lifecycle.runtime.compose)
    implementation(libs.coil.compose)
    implementation(libs.coil.network.ktor)
    implementation(libs.koin.android)
    implementation(libs.koin.compose)
    implementation("androidx.palette:palette-ktx:1.0.0")
}
