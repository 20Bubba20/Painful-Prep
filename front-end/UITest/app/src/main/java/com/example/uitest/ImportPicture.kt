package com.example.uitest

import android.os.Bundle
import androidx.activity.ComponentActivity
import android.widget.Button
import android.widget.Toast
import android.content.Intent
import android.util.Log
import androidx.activity.result.PickVisualMediaRequest
import androidx.activity.result.contract.ActivityResultContracts

/**
 *  This program class allows for a picture to be imported
 *  and sends the result to a server to run calculations.
 *  @author Jerron Pierro and Logan Johnson
 */
class ImportPicture : ComponentActivity() {
    private var uri: String? = null

    private val pickVisualMediaLauncher = registerForActivityResult(
        ActivityResultContracts.PickVisualMedia()
    ) { uri ->
        if (uri != null) {
            Log.d("PhotoPicker", "Selected URI: $uri")
            this.uri = uri.toString()
            val intent: Intent = Intent(this, Dimensions::class.java)
            intent.putExtra("photo", uri)
            startActivity(intent)
        } else {
            Log.d("PhotoPicker", "No media selected")
        }
    }

    /**
     *  This function starts the "ImportPicture" activity,
     *  and starts the camera on the device, if permissions are given.
     *  If no permissions are given, it prompts the user to allow camera access.
     *  @param savedInstanceState
     */
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.importpicturepage)

        /* Assign Buttons values */
        val toHome: Button = findViewById(R.id.index)
        val uploadPicture: Button = findViewById(R.id.uploadPicture)

        /* On the button press, jump to MainActivity.kt */
        toHome.setOnClickListener {
            val intent = Intent(this, MainActivity::class.java)
            startActivity(intent)
        }

        /* On the button press, open media selector  */
        uploadPicture.setOnClickListener {
            //Toast.makeText(this, "Upload Picture Clicked", Toast.LENGTH_LONG).show()
            val selectImage = PickVisualMediaRequest.Builder()
                .setMediaType(ActivityResultContracts.PickVisualMedia.ImageOnly)
                .build()
            pickVisualMediaLauncher.launch(selectImage)
        }
    }
}
