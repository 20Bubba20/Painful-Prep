package com.example.uitest

import android.content.Intent
import android.os.Bundle
import androidx.activity.ComponentActivity
import android.widget.Button
import android.widget.ImageView
import android.net.Uri
import android.util.Log

/**
 * This program shows the photo showing the modified photo from app.py.
 * Dimensions inherits from ComponentActivity().
 * @author Jerron Pierro
 */
class Dimensions : ComponentActivity() {
    /**
     *  This function starts the "Dimensions" activity,
     *  and will show the photo passed within the bundle.
     *  @param Bundle
     */
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.results)

        /* If the photoURI passed is not null, display it. */
        val photoURI: Uri? = intent.getParcelableExtra("photo")
        if (photoURI != null) {
            val imageView : ImageView = findViewById(R.id.imageView)
            imageView.setImageURI(photoURI)
        }
        else {
            Log.e("Dimensions", "could not load photo")
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
