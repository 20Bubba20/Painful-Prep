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

        val photoURI: Uri? = intent.getParcelableExtra("photo")
        if (photoURI != null) {
            val imageView : ImageView = findViewById(R.id.imageView)
            imageView.setImageURI(photoURI)
        } else {
            Log.e("Dimensions", "could not load photo")
        }

        // Extract JSON response from Intent
        val jsonString = intent.getStringExtra("response")
        val textView: TextView = findViewById(R.id.dimensionsView)

        if (!jsonString.isNullOrEmpty()) {
            try {
                val json = JSONObject(jsonString)
                val width = json.getDouble("width_in")
                val height = json.getDouble("height_in")
                textView.text = "Width: %.2f in\nHeight: %.2f in".format(width, height)
            } catch (e: Exception) {
                Log.e("Dimensions", "Failed to parse JSON", e)
                textView.text = "Could not locate markers!"
            }
        } else {
            textView.text = "No response received"
        }

        val toHome: Button = findViewById(R.id.index)
        toHome.setOnClickListener {
            val intent = Intent(this, MainActivity::class.java)
            startActivity(intent)
        }
    }
}
