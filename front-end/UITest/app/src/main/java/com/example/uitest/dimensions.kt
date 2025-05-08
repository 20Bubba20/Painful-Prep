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

/**
 * This program shows the photo showing the modified photo from app.py.
 * Dimensions inherits from ComponentActivity().
 * @author Jerron Pierro & Logan Johnson
 */
class Dimensions : ComponentActivity() {
    /**
     *  This function starts the "Dimensions" activity,
     *  and will show the photo passed within the bundle.
     *  @param savedInstanceState
     */
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.results)

        val imageView: ImageView = findViewById(R.id.imageView)
        val dimensionsView: TextView = findViewById(R.id.dimensionsView)

        /* If the photoURI passed is not null, display it. */
        val photoURI: Uri? = intent.getParcelableExtra("photo")
        if (photoURI != null) {
            imageView.setImageURI(photoURI)
        }
        else {
            Log.e("Dimensions", "could not load photo")
        }

        /* Load and parse JSON from the intent extras */
        val jsonString = intent.getStringExtra("response")

        /* Check if the JSON string is not null or empty */
        if (!jsonString.isNullOrEmpty()) {
            try {
                /* Convert the string into a JSONObject */
                val json = JSONObject(jsonString)

                /* Extract width and height values (in inches) from the JSON */
                val width = json.getDouble("width_in")
                val height = json.getDouble("height_in")

                /* Display the extracted dimensions with two decimal places */
                dimensionsView.text = "Width: %.2f in\nHeight: %.2f in".format(width, height)
            } catch (e: Exception) {
                /* Log and display an error message if parsing fails */
                Log.e("Dimensions", "Error parsing JSON", e)
                dimensionsView.text = "Error: Unable to detect markers!"
            }
        } else {
            /* Show a fallback message if no response was received */
            dimensionsView.text = "No response received"
        }

        /* Assign Buttons values */
        val toHome: Button = findViewById(R.id.index)

        /* On the button press, jump to MainActivity.kt */
        toHome.setOnClickListener {
            val intent: Intent = Intent(this, MainActivity::class.java)
            startActivity(intent)
        }
    }
}
