package com.example.uitest

import android.os.Bundle
import androidx.activity.ComponentActivity
import android.widget.Button
import android.widget.Toast
import android.content.Intent
import android.util.Log
import androidx.activity.result.PickVisualMediaRequest
import androidx.activity.result.contract.ActivityResultContracts
import okhttp3.*
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import kotlinx.coroutines.*
import android.net.Uri
import java.util.concurrent.TimeUnit


class ImportPicture : ComponentActivity() {

    private var uri: String? = null

    private val pickVisualMediaLauncher = registerForActivityResult(
    ActivityResultContracts.PickVisualMedia()
    ) { uri ->
        if (uri != null) {
            Log.d("PhotoPicker", "Selected URI: $uri")
            this.uri = uri.toString()

            // Log starting the upload
            Log.d("UploadFlow", "Starting coroutine to upload image")

            CoroutineScope(Dispatchers.IO).launch {
                try {
                    val response = uploadToFlask(uri)

                    // Log when response is received
                    Log.d("UploadFlow", "Received response: $response")

                    withContext(Dispatchers.Main) {
                        Toast.makeText(this@ImportPicture, response ?: "Error", Toast.LENGTH_LONG).show()

                        val intent = Intent(this@ImportPicture, dimensions::class.java)
                        intent.putExtra("response", response)
                        startActivity(intent)
                    }
                } catch (e: Exception) {
                    Log.e("UploadError", "Exception during upload", e)
                    withContext(Dispatchers.Main) {
                        Toast.makeText(this@ImportPicture, "Upload failed: ${e.message}", Toast.LENGTH_LONG).show()
                    }
                }
            }
        } else {
            Log.d("PhotoPicker", "No media selected")
        }
    }


    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.importpicturepage)

        val toHome: Button = findViewById(R.id.index)
        val uploadPicture: Button = findViewById(R.id.uploadPicture)

        toHome.setOnClickListener {
            val intent = Intent(this, MainActivity::class.java)
            startActivity(intent)
        }

        uploadPicture.setOnClickListener {
            Toast.makeText(this, "Upload Picture Clicked", Toast.LENGTH_LONG).show()
            val selectImage = PickVisualMediaRequest.Builder()
                .setMediaType(ActivityResultContracts.PickVisualMedia.ImageOnly)
                .build()
            pickVisualMediaLauncher.launch(selectImage)
        }
    }

    private suspend fun uploadToFlask(uri: Uri): String? {
        Log.d("UploadToFlask", "Preparing file from URI: $uri")

        val stream = contentResolver.openInputStream(uri)
        val fileBytes = stream?.use { it.readBytes() } ?: return null

        Log.d("UploadToFlask", "Read ${fileBytes.size} bytes from file")

        val requestBody = MultipartBody.Builder().setType(MultipartBody.FORM)
            .addFormDataPart(
                "image", "upload.jpg",
                RequestBody.create("image/jpeg".toMediaTypeOrNull(), fileBytes)
            )
            .addFormDataPart("marker_size", "50")
            .build()

        val client = OkHttpClient.Builder()
            .connectTimeout(10, TimeUnit.SECONDS)
            .writeTimeout(10, TimeUnit.SECONDS)
            .readTimeout(10, TimeUnit.SECONDS)
            .build()

        val request = Request.Builder()
            .url("http://10.0.2.2:5000/detect") //Change this if using an Andorid device
            .post(requestBody)
            .build()

        Log.d("UploadToFlask", "Sending request to Flask server")

        val response = client.newCall(request).execute()

        Log.d("UploadToFlask", "Received HTTP ${response.code}")

        return response.body?.string().also {
            Log.d("UploadToFlask", "Response body: $it")
        }
    }

}
