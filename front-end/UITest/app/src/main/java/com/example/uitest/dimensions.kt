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

class dimensions : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        //enableEdgeToEdge()

        /* Set layout to index page */
        setContentView(R.layout.results)
        val uploadPicture: Button = findViewById(R.id.index)
    }
}
