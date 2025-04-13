package com.example.uitest

import android.os.Bundle
import androidx.activity.ComponentActivity
import android.widget.Button
import android.widget.Toast
import android.content.Intent
import android.util.Log
import androidx.activity.result.PickVisualMediaRequest
import androidx.activity.result.contract.ActivityResultContracts

//import androidx.appcompat.app.AppCompatActivity

class ImportPicture : ComponentActivity() {
    private lateinit var pickVisualMedia: ActivityResultContracts.PickVisualMedia
    private var uri: String? = null
    override fun onCreate(savedInstanceState: Bundle?) {
        // val pickVisualMedia: ActivityResultContracts.PickVisualMedia


        super.onCreate(savedInstanceState)
        //enableEdgeToEdge()
        val pickVisualMediaLauncher = registerForActivityResult(
            ActivityResultContracts.PickVisualMedia()
        ) { uri ->
            if (uri != null) {
                Log.d("PhotoPicker", "Selected URI: $uri")
                this.uri = uri.toString()
                val intent: Intent = Intent(this, dimensions::class.java)
                intent.putExtra("photo", uri)
                startActivity(intent)
            } else {
                Log.d("PhotoPicker", "No media selected")
            }
        }
        /* Set layout to index page */
        setContentView(R.layout.importpicturepage)
        val toHome: Button = findViewById(R.id.index)

        val uploadPicture: Button = findViewById(R.id.uploadPicture)

        toHome.setOnClickListener {
            val intent: Intent = Intent(this, MainActivity::class.java)
            startActivity(intent)
        }

        uploadPicture.setOnClickListener {
            Toast.makeText(this, "Upload Picture Clicked", Toast.LENGTH_LONG).show()
            val selectImage = PickVisualMediaRequest.Builder().setMediaType(ActivityResultContracts.PickVisualMedia.ImageOnly).build()
            pickVisualMediaLauncher.launch(selectImage)

        }

    }
}
