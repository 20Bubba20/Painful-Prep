package com.example.uitest

import android.content.Intent
import android.os.Bundle
import androidx.activity.ComponentActivity
import android.widget.Button
import androidx.core.net.toUri
import android.widget.ImageView
import android.net.Uri
import androidx.compose.foundation.Image
import android.util.Log
import android.widget.TextView
import org.json.JSONObject

class dimensions : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.results)

        val imageView: ImageView = findViewById(R.id.imageView)
        val dimensionsView: TextView = findViewById(R.id.dimensionsView)

        // Load image
        val photoURI: Uri? = intent.getParcelableExtra("photo")
        if (photoURI != null) {
            imageView.setImageURI(photoURI)
        } else {
            Log.e("Dimensions", "No photo URI received")
        }

        // Load and parse JSON
        val jsonString = intent.getStringExtra("response")
        if (!jsonString.isNullOrEmpty()) {
            try {
                val json = JSONObject(jsonString)
                val width = json.getDouble("width_in")
                val height = json.getDouble("height_in")
                dimensionsView.text = "Width: %.2f in\nHeight: %.2f in".format(width, height)
            } catch (e: Exception) {
                Log.e("Dimensions", "Error parsing JSON", e)
                dimensionsView.text = "Error: Unable to detect markers!"
            }
        } else {
            dimensionsView.text = "No response received"
        }

        // Button to return home
        val toHome: Button = findViewById(R.id.index)
        toHome.setOnClickListener {
            val intent = Intent(this, MainActivity::class.java)
            startActivity(intent)
        }
    }
}
