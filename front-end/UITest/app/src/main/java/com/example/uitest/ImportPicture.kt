package com.example.uitest

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.tooling.preview.Preview
import com.example.uitest.ui.theme.UITestTheme
import android.widget.Button
import android.widget.Toast
import android.content.Intent
//import androidx.appcompat.app.AppCompatActivity


class ImportPicture : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        //enableEdgeToEdge()

        /* Set layout to index page */
        setContentView(R.layout.importpicturepage)
        val toHome: Button = findViewById(R.id.index)
        /* TODO: Everything */
        /* Assign Buttons values */
        //val takePicture: Button = findViewById(R.id.__)
        //val uploadPicture: Button = findViewById(R.id.__)

        toHome.setOnClickListener {
            val intent: Intent = Intent(this, MainActivity::class.java)
            startActivity(intent)
        }
        /*
        uploadPicture.setOnClickListener {
            Toast.makeText(this, "Upload Picture Clicked", Toast.LENGTH_LONG).show()
        }
        */
    }
}
