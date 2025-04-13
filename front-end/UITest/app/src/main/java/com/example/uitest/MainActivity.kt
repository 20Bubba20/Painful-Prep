package com.example.uitest

import android.content.Intent
import android.os.Bundle
import androidx.activity.ComponentActivity
import android.widget.Button
import android.Manifest
import android.app.Activity
import android.content.Context
import android.content.pm.PackageManager
import android.os.Build
import android.widget.Toast
import androidx.activity.result.ActivityResultLauncher
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import java.security.Permission


class MainActivity : AppCompatActivity() /* ComponentActivity() */ {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        /* Set layout to index page */
        setContentView(R.layout.index)

        /* Assign Buttons values */
        val takePicture: Button = findViewById(R.id.TakePicture)
        val uploadPicture: Button = findViewById(R.id.uploadPicture)

        /* When the takePicture button is clicked, move to the take picture screen */
        takePicture.setOnClickListener {
            //Toast.makeText(this, "Button Clicked", Toast.LENGTH_LONG).show()
            val intent: Intent = Intent(this, TakePicture::class.java)
            startActivity(intent)
        }
        /* When the uploadPicture button is clicked, move to the take picture screen */
        uploadPicture.setOnClickListener {
            val intent: Intent = Intent(this, ImportPicture::class.java)
            startActivity(intent)
        }

    }
    object Shared {
        private var permissionReqInProgress = false

        fun requestPermissions(activity: Activity, launcher: ActivityResultLauncher<Array<String>>) {
            if (!permissionReqInProgress) {
                permissionReqInProgress = true
                launcher.launch(REQUIRED_PERMISSIONS)
                permissionReqInProgress = false
            }


        }

        fun allPermissionsGranted(context: Context) = REQUIRED_PERMISSIONS.all {
            ContextCompat.checkSelfPermission(context, it) == PackageManager.PERMISSION_GRANTED
        }

        fun handlePermissionsResults(context: Context, permissions: Map<String, Boolean>) {
            val permissionsGranted = REQUIRED_PERMISSIONS.all { permissions[it] == true }
            if (!permissionsGranted) {
                Toast.makeText(context, "Permission request denied", Toast.LENGTH_SHORT).show()
            }
        }
    }

    val activityResultLauncher = registerForActivityResult(ActivityResultContracts.RequestMultiplePermissions()) {
            permissions ->

        var permissionsGranted = true
        permissions.entries.forEach {
            if (it.key in MainActivity.Companion. REQUIRED_PERMISSIONS && !it.value) {
                permissionsGranted = false
            }
        }
        if (!permissionsGranted) {
            Toast.makeText(baseContext, "Permission request denied", Toast.LENGTH_SHORT).show()
        }

    }

    companion object {
        const val TAG = "Painless Prep App"
        const val FILENAME_FORMAT = "MM-dd-yyyy-HH-mm-ss"
        val REQUIRED_PERMISSIONS =
            mutableListOf(
                Manifest.permission.CAMERA
                //Manifest.permission.READ_EXTERNAL_STORAGE
            ).apply {
                if (Build.VERSION.SDK_INT <= Build.VERSION_CODES.P) {
                    add(Manifest.permission.WRITE_EXTERNAL_STORAGE)
                }
            }.toTypedArray()
    }
}

