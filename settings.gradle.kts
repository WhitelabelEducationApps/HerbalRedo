rootProject.name = "HerbalRedo"

include(":androidApp")
include(":shared")

includeBuild("whitelabel-core")
includeBuild("whitelabel-platform")

pluginManagement {
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
        mavenCentral()
        maven("https://maven.pkg.jetbrains.space/public/p/compose/dev")
    }
}

dependencyResolutionManagement {
    repositories {
        google()
        mavenCentral()
    }
}
