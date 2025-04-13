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

class dimensions : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.results)
        //enableEdgeToEdge()

        //val uriString = intent.getStringExtra("photo")
        //val uri = uriString?.toUri()
        //val uri = uriString?.let{Uri.parse(it)
        //val bundle: Bundle? = intent.extras
        //val photoURIString = bundle?.getString("photo")
        //val uri = photoURIString?.toUri()
        //val uri = intent.extras?.getString("photo")?.toUri()
        val photoURI: Uri? = intent.getParcelableExtra("photo")
        if (photoURI != null) {
            val imageView : ImageView = findViewById(R.id.imageView)
            imageView.setImageURI(photoURI)
        }
        else {
            Log.e("Dimensions", "could not load photo")
        }
       // val imageView : ImageView = findViewById(R.id.imageView)

        /* Set layout to index page */
        //setContentView(R.layout.results)
        //imageView.setImageURI(uri)
        //val imageView: ImageView = findViewById(R.id.imageView)
        //imageView.setImageURI(uri)
        val toHome: Button = findViewById(R.id.index)

        toHome.setOnClickListener {
            val intent: Intent = Intent(this, MainActivity::class.java)
            startActivity(intent)
        }
    }
}
