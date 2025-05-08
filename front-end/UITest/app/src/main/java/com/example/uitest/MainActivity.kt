package com.example.uitest

import android.content.Intent
import android.os.Bundle
import android.widget.Button
import android.widget.EditText
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

/**
 * This program is the base page for the Painless Prep application.
 * This allows the user to jump to either TakePicture.kt or ImportPicture.kt.
 * This page is where permissions are originally prompted, and saved.
 * @author Jerron Pierro
 */
class MainActivity : AppCompatActivity() {
    /**
     *  This function starts the "MainActivity" activity,
     *  and will show the photo passed within the bundle.
     *  @param savedInstanceState
     */
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        /* Set layout to index page */
        setContentView(R.layout.index)

        /* Assign Buttons values */
        val takePicture: Button = findViewById(R.id.TakePicture)
        val uploadPicture: Button = findViewById(R.id.uploadPicture)

        /* When the takePicture button is clicked, move to the take picture screen */
        takePicture.setOnClickListener {
            /* assign textBox value, if none, set to 1.1.1.1 */
            val textBox: EditText = findViewById(R.id.ip)
            if (textBox.text.isNullOrEmpty()) {
                textBox.setText("1.1.1.1")
            }

            val intent = Intent(this, TakePicture::class.java)
            intent.putExtra("Server", textBox.text.toString())
            startActivity(intent)
        }

        /* When the uploadPicture button is clicked, move to the take picture screen */
        uploadPicture.setOnClickListener {
            /* assign textBox value, if none, set to 1.1.1.1 */
            val textBox: EditText = findViewById(R.id.ip)
            if (textBox.text.isNullOrEmpty()) {
                textBox.setText("1.1.1.1")
            }

            val intent = Intent(this, ImportPicture::class.java)
            intent.putExtra("Server", (textBox.text).toString())
            startActivity(intent)
        }

    }

    /**
     * Shared object to pass resources across the needed activities.
     */
    object Shared {
        private var permissionReqInProgress = false

        /**
         * This function requests permissions for the Painless Prep application, if none are given.
         * @param activity - The Activity calling the function
         * @param launcher - ActivityResultLauncher from the calling function
         */
        fun requestPermissions(activity: Activity, launcher: ActivityResultLauncher<Array<String>>) {
            if (!permissionReqInProgress) {
                permissionReqInProgress = true
                launcher.launch(REQUIRED_PERMISSIONS)
            }
        }

        /**
         * This function verifies all permissions are granted.
         * @param context - Context of this running application.
         */
        fun allPermissionsGranted(context: Context) = REQUIRED_PERMISSIONS.all {
            ContextCompat.checkSelfPermission(context, it) == PackageManager.PERMISSION_GRANTED
        }

        /**
         * This function handles gathering the permissions.
         * @param context - Context of this running app
         * @param permissions - All permissions required
         */
        fun handlePermissionsResults(context: Context, permissions: Map<String, Boolean>) {
            val permissionsGranted = REQUIRED_PERMISSIONS.all { permissions[it] == true }
            if (!permissionsGranted) {
                Toast.makeText(context, "Permission request denied", Toast.LENGTH_SHORT).show()
            }

            permissionReqInProgress = false
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

    /**
     * The data for naming the photo taken in TakePicture.kt
     */
    companion object {
        const val TAG = "Painless Prep App"
        const val FILENAME_FORMAT = "MM-dd-yyyy-HH-mm-ss"
        val REQUIRED_PERMISSIONS =
            mutableListOf(
                Manifest.permission.CAMERA
                //Manifest.permission.INTERNET
                //Manifest.permission.READ_EXTERNAL_STORAGE
            ).apply {
                if (Build.VERSION.SDK_INT <= Build.VERSION_CODES.P) {
                    add(Manifest.permission.WRITE_EXTERNAL_STORAGE)
                }
            }.toTypedArray()
    }
}

