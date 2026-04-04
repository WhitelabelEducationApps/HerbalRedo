# Whitelabel KMP Core

A reusable Kotlin Multiplatform core library for building catalog-based mobile applications with multilingual support and modern UI components.

## 🎯 Purpose

The **Whitelabel KMP Core** provides generic abstractions, reusable UI components, and common functionality for building catalog-style applications (museums, galleries, collections, etc.) with Kotlin Multiplatform. It's designed to be the foundation for multiple whitelabel applications.

## 🏗️ Architecture

### Core Abstractions

#### Generic Domain Models
- **`DisplayableItem`** - Universal interface for any catalog item
  - Supports multilingual content with `LocalizedFieldSet`
  - Includes metadata: images, colors, coordinates, favorites
  - Provides localized getters for names, descriptions, categories

#### Repository Contracts
- **`ItemRepository<T>`** - Generic repository interface
  - Reactive data access with `Flow<Result<T>>`
  - Standard CRUD operations for catalog items
  - Search and favorites functionality
  - Grouping and metadata support

#### Language Support
- **`SupportedLanguage`** - Enum with 16 languages
  - Complete language metadata (code, display name, native name)
  - Runtime language switching support
  - Fallback to English for unsupported languages

### Reusable UI Components

#### Generic Components
- **`ItemCard<T>`** - Universal card component for any item
  - Customizable colors and image height
  - Favorite toggle with animations
  - Responsive layout with Material 3 design
  - Image loading with Coil integration

#### Common UI Elements
- **`EmptyState`** - Consistent empty state handling
- **`LoadingIndicator`** - Standardized loading UI
- **`SearchTopAppBar`** - Search functionality
- **`MarqueeText`** - Text scrolling for long content

### Domain Layer

#### Use Cases
- **`GetItemsUseCase`** - Retrieve catalog items
- **`GetItemDetailUseCase`** - Get item details by ID
- **`SearchItemsUseCase`** - Multilingual search functionality
- **`ToggleFavoriteUseCase`** - Favorites management

#### Services
- **`WallpaperService`** - Platform abstraction for wallpaper setting
  - `expect`/`actual` implementation for platform-specific code
  - Android implementation available, iOS ready

### Presentation Layer

#### Base Classes
- **`ViewModel`** - Base ViewModel with StateFlow support
  - Generic state management patterns
  - Error handling and loading states

#### Screens
- **`ItemDetailScreen`** - Generic item detail view
  - Zoomable image viewer
  - Favorite management
  - Multilingual content display

- **`LanguageSelectionScreen`** - Dynamic language switching
  - Runtime language change
  - Persistent language preferences

#### Theming
- **`AppThemeConfig`** - Customizable theme configuration
  - Light/dark theme colors
  - Material 3 design system integration
  - Dynamic theming support

## 📱 Platform Support

### Kotlin Multiplatform Targets
- **Android** - Full implementation with platform-specific features
- **iOS** - Framework generation configured, ready for implementation
- **Desktop/Web** - Prepared for future expansion

### Platform-Specific Features
- **Android**: Google Maps integration, wallpaper setting, image preprocessing
- **iOS**: Platform abstractions defined, implementation ready
- **Common**: Shared UI components, business logic, data models

## 🛠️ Integration Guide

### Adding to Your Project

1. **Include as Git Submodule**
   ```bash
   git submodule add https://github.com/your-org/whitelabel-kmp-core.git whitelabel-core
   ```

2. **Add to Settings**
   ```kotlin
   // settings.gradle.kts
   includeBuild("whitelabel-core")
   ```

3. **Add Dependency**
   ```kotlin
   // shared/build.gradle.kts
   implementation("com.whitelabel:core:0.1.0")
   ```

### Implementing the Core

#### Step 1: Implement DisplayableItem
```kotlin
data class YourItem(
    override val id: Long,
    override val name: String,
    override val description: String?,
    override val imageUrls: List<String>,
    override val category: String?,
    override val groupKey: String?,
    override val isFavorite: Boolean,
    override val wasViewed: Boolean,
    override val latitude: Double?,
    override val longitude: Double?,
    override val primaryColor: Int?,
    override val secondaryColor: Int?,
    override val backgroundColor: Int?,
    override val detailColor: Int?,
    override val localizedFields: LocalizedFieldSet
) : DisplayableItem
```

#### Step 2: Implement Repository
```kotlin
class YourRepository : ItemRepository<YourItem> {
    override fun getAllItems(): Flow<Result<List<YourItem>>> {
        // Your implementation
    }
    
    // Implement other required methods...
}
```

#### Step 3: Configure Theme
```kotlin
val appThemeConfig = AppThemeConfig(
    lightPrimary = Color(0xFF1976D2),
    lightOnPrimary = Color.White,
    // Configure other colors...
)
```

#### Step 4: Use Components
```kotlin
@Composable
fun YourScreen() {
    ItemCard(
        item = yourItem,
        languageCode = "en",
        onClick = { /* Handle click */ },
        onFavoriteClick = { /* Handle favorite */ }
    )
}
```

## 🌍 Multilingual Support

### Supported Languages
The core library supports 16 languages out of the box:

| Code | Language | Native Name |
|------|----------|-------------|
| en | English | English |
| fr | French | Français |
| es | Spanish | Español |
| de | German | Deutsch |
| it | Italian | Italiano |
| pt | Portuguese | Português |
| ru | Russian | Русский |
| ar | Arabic | العربية |
| zh | Chinese | 中文 |
| ja | Japanese | 日本語 |
| ro | Romanian | Română |
| tr | Turkish | Türkçe |
| hi | Hindi | हिन्दी |
| hu | Hungarian | Magyar |
| pl | Polish | Polski |
| nl | Dutch | Nederlands |

### Localization Implementation
```kotlin
// Get localized content
val localizedName = item.getLocalizedName(languageCode)
val localizedDescription = item.getLocalizedDescription(languageCode)
val localizedCategory = item.getLocalizedCategory(languageCode)
```

## 🎨 UI Components

### ItemCard Features
- **Responsive Design**: Adapts to different screen sizes
- **Image Loading**: Automatic caching and error handling
- **Favorite Toggle**: Animated favorite button
- **Customizable**: Colors, image height, card styling
- **Accessibility**: Proper content descriptions and semantics

### Example Usage
```kotlin
ItemCard(
    item = heritageSite,
    languageCode = currentLanguage.code,
    onClick = { navigateToDetail(heritageSite.id) },
    onFavoriteClick = { viewModel.toggleFavorite(heritageSite) },
    cardColors = CardDefaults.cardColors(
        containerColor = MaterialTheme.colorScheme.surface
    ),
    imageHeight = 140.dp
)
```

## 📦 Dependencies

### Core Dependencies
- **Compose Multiplatform** - UI framework
- **Kotlin Coroutines** - Asynchronous programming
- **Koin** - Dependency injection
- **Coil** - Image loading
- **Kermit** - Logging

### Platform Dependencies
- **Android**: Coil, Ktor, Android-specific libraries
- **iOS**: Native SQLDelight driver
- **Common**: Shared business logic and UI

## 🔧 Development Guidelines

### Code Conventions
- **Generic Types**: Use `<T : DisplayableItem>` for type safety
- **Null Safety**: Leverage Kotlin's null safety features
- **Reactive Programming**: Use Flow for data streams
- **Composition**: Prefer composition over inheritance

### File Organization
```
whitelabel-core/
├── core/
│   └── src/
│       ├── commonMain/kotlin/com/whitelabel/core/
│       │   ├── domain/          # Domain models and contracts
│       │   ├── presentation/    # UI components and screens
│       │   └── theme/          # Theme configuration
│       ├── androidMain/        # Android-specific implementations
│       └── iosMain/           # iOS-specific implementations
```

### Best Practices
- **Type Safety**: Use generic types for compile-time safety
- **Separation of Concerns**: Keep domain, presentation, and platform separate
- **Reactive Design**: Use Flow for reactive data streams
- **Accessibility**: Include proper semantics and content descriptions

## 🚀 Version History

### v0.1.0 (Current)
- Initial release with core abstractions
- Generic UI components
- Multilingual support for 16 languages
- Android platform implementation
- iOS framework generation

### Planned Features
- **v0.2.0**: Enhanced search capabilities, filtering
- **v0.3.0**: Advanced animations and transitions
- **v0.4.0**: Desktop and Web platform support
- **v0.5.0**: Advanced theming and customization

## 📄 License

This library is designed for educational and commercial use in building catalog-based applications.

## 🤝 Contributing

Contributions are welcome! Please ensure:
- Code follows the established conventions
- New features are generic and reusable
- Documentation is updated for new features
- Tests are included for new functionality

---

**Library Status**: ✅ Production Ready  
**Version**: 0.1.0  
**Supported Platforms**: Android (Full), iOS (Ready)  
**Languages**: 16 supported  
**Last Updated**: April 2026
