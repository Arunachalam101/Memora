// FlaskService.java - Background service to run Flask server
package org.memora.app;

import android.app.Service;
import android.content.Intent;
import android.os.IBinder;
import android.util.Log;
import java.io.File;

import com.chaquo.python.Python;
import com.chaquo.python.PyObject;

public class FlaskService extends Service {
    private static final String TAG = "MEMORA.FlaskService";

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        Log.d(TAG, "Flask service starting");
        
        // Start Flask in a new thread
        new Thread(() -> {
            try {
                // Get app data directory
                File appDataDir = getFilesDir();
                File databaseDir = new File(appDataDir, "data");
                databaseDir.mkdirs();
                File uploadsDir = new File(appDataDir, "uploads");
                uploadsDir.mkdirs();
                
                Log.d(TAG, "App data dir: " + appDataDir.getAbsolutePath());
                
                // Start embedded Python (Chaquopy) - real MEMORA Flask application
                Python py = Python.getInstance();
                PyObject launcher = py.getModule("android_launcher");
                launcher.callAttr("start", appDataDir.getAbsolutePath());
                
                Log.d(TAG, "Flask service initialization complete");
                
            } catch (Exception e) {
                Log.e(TAG, "Error starting Flask", e);
            }
        }).start();
        
        return START_STICKY;
    }

    @Override
    public void onDestroy() {
        super.onDestroy();
        Log.d(TAG, "Flask service destroying");
    }

    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }
}
