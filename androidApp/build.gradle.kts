import java.util.Properties
import java.io.FileInputStream
import javax.inject.Inject
import org.gradle.process.ExecOperations

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
    implementation(platform(libs.androidx.compose.bom))
    implementation(libs.androidx.compose.ui)
    implementation(libs.androidx.compose.material3)
    implementation(libs.androidx.activity.compose)
    implementation(libs.androidx.lifecycle.runtime.compose)
    implementation(libs.coil.compose)
    implementation(libs.coil.network.ktor)
    implementation(libs.koin.android)
    implementation(libs.koin.compose)
    implementation(libs.androidx.palette.ktx)
}

// ── Pre-extract plant colors at build time ───────────────────────────────────
// Custom task type so AGP's Variant API can wire it as a generated asset
// source — no manual dependsOn needed for any lint/merge/model task.

abstract class ExtractColorsTask @Inject constructor(
    private val execOps: ExecOperations
) : DefaultTask() {

    @get:InputDirectory
    @get:PathSensitive(PathSensitivity.RELATIVE)
    abstract val drawableDir: DirectoryProperty

    @get:InputFile
    @get:PathSensitive(PathSensitivity.NONE)
    abstract val scriptFile: RegularFileProperty

    @get:OutputDirectory
    abstract val outputDir: DirectoryProperty

    @get:Input
    abstract val pythonCmd: Property<String>

    @TaskAction
    fun run() {
        val outDir = outputDir.get().asFile
        outDir.mkdirs()
        execOps.exec {
            commandLine(
                pythonCmd.get(),
                scriptFile.get().asFile.absolutePath,
                "--drawable-dir", drawableDir.get().asFile.absolutePath,
                "--output",       java.io.File(outDir, "extracted_colors.json").absolutePath
            )
        }
    }
}

val extractColors = tasks.register<ExtractColorsTask>("extractColors") {
    description = "Pre-extract dominant colors from plant drawables (requires: pip install Pillow)"
    group = "build"
    pythonCmd.set(if (System.getProperty("os.name").lowercase().contains("windows")) "python" else "python3")
    scriptFile.set(rootProject.file("scripts/extract_colors.py"))
    drawableDir.set(file("src/main/res/drawable-nodpi"))
    outputDir.set(layout.buildDirectory.dir("generated/extractColors"))
}

// addGeneratedSourceDirectory properly wires extractColors into every
// AGP task that consumes assets (mergeAssets, lintVital*, model writers…).
androidComponents {
    onVariants { variant ->
        variant.sources.assets?.addGeneratedSourceDirectory(extractColors) { it.outputDir }
    }
}
