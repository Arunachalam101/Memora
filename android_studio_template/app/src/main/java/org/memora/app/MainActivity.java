// MainActivity.java - WebView + Flask Launcher for MEMORA
package org.memora.app;

import android.app.Activity;
import android.os.Build;
import android.os.Bundle;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.net.Uri;
import android.content.Intent;
import android.util.Log;

import java.io.File;
import java.io.IOException;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.concurrent.TimeUnit;

public class MainActivity extends Activity {
    private static final String TAG = "MEMORA";
    private static final String BASE_URL = "http://127.0.0.1:5000";
    private static final String ENTRY_URL = BASE_URL + "/";
    private WebView webView;
    private FlaskService flaskService;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        Log.d(TAG, "MEMORA MainActivity starting");

        // Initialize WebView
        webView = findViewById(R.id.webview);
        configureWebView();

        // Start Flask server in background service
        startFlaskServer();

        // Poll until Flask responds, then load the real MEMORA app (avoids arbitrary sleep)
        waitForFlaskThenLoad();
    }

    private void waitForFlaskThenLoad() {
        new Thread(() -> {
            boolean ready = false;
            for (int i = 0; i < 50; i++) { // up to ~15s
                try {
                    HttpURLConnection conn = (HttpURLConnection) new URL(BASE_URL + "/login").openConnection();
                    conn.setConnectTimeout(300);
                    conn.setReadTimeout(300);
                    int code = conn.getResponseCode();
                    conn.disconnect();
                    if (code > 0) {
                        ready = true;
                        break;
                    }
                } catch (IOException e) {
                    // Not ready yet
                }
                try {
                    Thread.sleep(300);
                } catch (InterruptedException ignored) {
                }
            }
            final boolean finalReady = ready;
            runOnUiThread(() -> {
                if (finalReady) {
                    loadMemoraApp();
                } else {
                    Log.e(TAG, "Flask did not become ready in time");
                    webView.loadData(
                        "<html><body><h1>MEMORA is taking longer than expected to start</h1></body></html>",
                        "text/html", "utf-8"
                    );
                }
            });
        }).start();
    }

    private void configureWebView() {
        WebSettings settings = webView.getSettings();
        
        // Enable JavaScript
        settings.setJavaScriptEnabled(true);
        
        // Enable DOM storage
        settings.setDomStorageEnabled(true);
        settings.setDatabaseEnabled(true);
        
        // Enable local networking
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
            settings.setMixedContentMode(WebSettings.MIXED_CONTENT_ALWAYS_ALLOW);
        }
        
        // Set user agent
        settings.setUserAgentString(settings.getUserAgentString() + " MEMORA/1.0");
        
        // WebView client for error handling and keeping navigation on localhost only
        webView.setWebViewClient(new WebViewClient() {
            @Override
            public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                String url = request.getUrl().toString();
                if (url.startsWith(BASE_URL)) {
                    return false; // allow
                }
                Log.d(TAG, "Blocked external navigation to " + url);
                return true; // block
            }

            @Override
            public void onReceivedError(WebView view, int errorCode, String description, String failingUrl) {
                Log.e(TAG, "WebView error: " + description);
                webView.loadData(
                    "<html><body><h1>Error Loading MEMORA</h1>" +
                    "<p>" + description + "</p>" +
                    "<p>Make sure Flask server is running on http://127.0.0.1:5000</p></body></html>",
                    "text/html", "utf-8"
                );
            }
        });
        
        // Chrome client for debugging (optional)
        webView.setWebChromeClient(new WebChromeClient());
    }

    private void startFlaskServer() {
        Log.d(TAG, "Starting Flask server service");
        Intent serviceIntent = new Intent(this, FlaskService.class);
        startService(serviceIntent);
    }

    private void loadMemoraApp() {
        Log.d(TAG, "Loading MEMORA app from " + ENTRY_URL);
        webView.loadUrl(ENTRY_URL);
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        // Stop Flask server when app closes
        Intent serviceIntent = new Intent(this, FlaskService.class);
        stopService(serviceIntent);
    }

    @Override
    public void onBackPressed() {
        if (webView.canGoBack()) {
            webView.goBack();
        } else {
            super.onBackPressed();
        }
    }
}
