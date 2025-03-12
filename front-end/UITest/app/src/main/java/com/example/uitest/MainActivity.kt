package com.example.uitest

import android.content.Intent
import android.os.Bundle
import androidx.activity.ComponentActivity
import android.widget.Button


class MainActivity : ComponentActivity() {
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

}

