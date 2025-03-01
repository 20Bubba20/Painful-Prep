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
//import androidx.appcompat.app.AppCompatActivity


class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        //enableEdgeToEdge()
        setContentView(R.layout.layout)
        val takePicture: Button = findViewById(R.id.takePicture)

        takePicture.setOnClickListener {
            Toast.makeText(this, "Button Clicked", Toast.LENGTH_LONG).show()
        }

        /*setContent {
            UITestTheme {
                Scaffold(modifier = Modifier.fillMaxSize()) { innerPadding ->
                    Greeting(
                        name = "Jerron",
                        modifier = Modifier.padding(innerPadding)
                    )
                }
            }
        }*/
    }
}

@Composable
fun Greeting(name: String, modifier: Modifier = Modifier) {
    Text(
        text = "Hello $name!",
        modifier = modifier
    )
}

@Preview(showBackground = true)
@Composable
fun GreetingPreview() {
    UITestTheme {
        Greeting("Android")
    }
}