package com.example.uitest

import android.os.Bundle
import androidx.activity.ComponentActivity
import android.widget.Button
import android.content.Intent


class TakePicture : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        //enableEdgeToEdge()

        /* Set layout to index page
         * TODO: Everything
         */
        setContentView(R.layout.importpicturepage)
        val toHome: Button = findViewById(R.id.index)
        /* Assign Buttons values */

        toHome.setOnClickListener {
            val intent: Intent = Intent(this, MainActivity::class.java)
            startActivity(intent)
        }
    }
}
