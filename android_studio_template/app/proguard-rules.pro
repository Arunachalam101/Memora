# ProGuard rules for MEMORA

# Keep all classes in org.memora.app package
-keep class org.memora.app.** { *; }

# Keep MainActivity and FlaskService
-keep class org.memora.app.MainActivity { *; }
-keep class org.memora.app.FlaskService { *; }

# Keep AndroidX
-keep class androidx.** { *; }
-keep interface androidx.** { *; }

# Keep WebView classes
-keep class android.webkit.** { *; }

# Keep Java runtime classes
-keepnames class * extends android.app.Service
-keepnames class * extends android.app.Activity

# Preserve line numbers for debugging
-keepattributes SourceFile,LineNumberTable
-renamesourcefileattribute SourceFile
