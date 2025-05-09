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

/**
 *  This program class allows for a picture to be imported
 *  and sends the result to a server to run calculations.
 *  @author Jerron Pierro and Logan Johnson
 */
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

                        val intent = Intent(this@ImportPicture, Dimensions::class.java)
                        intent.putExtra("photo", uri)
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

    /**
     *  This function starts the "ImportPicture" activity,
     *  and starts the camera on the device, if permissions are given.
     *  If no permissions are given, it prompts the user to allow camera access.
     *  @param savedInstanceState
     */
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.importpicturepage)

        /* Assign Buttons values */
        val toHome: Button = findViewById(R.id.index)
        val uploadPicture: Button = findViewById(R.id.uploadPicture)

        /* On the button press, jump to MainActivity.kt */
        toHome.setOnClickListener {
            val intent = Intent(this, MainActivity::class.java)
            startActivity(intent)
        }

        /* On the button press, open media selector  */
        uploadPicture.setOnClickListener {
            //Toast.makeText(this, "Upload Picture Clicked", Toast.LENGTH_LONG).show()
            val selectImage = PickVisualMediaRequest.Builder()
                .setMediaType(ActivityResultContracts.PickVisualMedia.ImageOnly)
                .build()
            pickVisualMediaLauncher.launch(selectImage)
        }
    }

    /**
    * Uploads an image to a Flask backend and returns the response as a string.
    */
    private suspend fun uploadToFlask(uri: Uri): String? {
        /* Log the URI being used */
        Log.d("UploadToFlask", "Preparing file from URI: $uri")

        /* Open the image as a byte stream and read all bytes; return null if failed */
        val stream = contentResolver.openInputStream(uri)
        val fileBytes = stream?.use { it.readBytes() } ?: return null

        /* Get the server IP address from the intent extras */
        val ip = intent.extras?.getString("Server").toString()

        Log.d("UploadToFlask", "Read ${fileBytes.size} bytes from file")

        /* Build a multipart/form-data request with the image and a marker size parameter */
        val requestBody = MultipartBody.Builder().setType(MultipartBody.FORM)
            .addFormDataPart(
                "image", "upload.jpg",
                RequestBody.create("image/jpeg".toMediaTypeOrNull(), fileBytes)
            )
            .addFormDataPart("marker_size", "50")
            .build()

        /* Build an HTTP client with timeout settings and permissive hostname verification */
        val client = OkHttpClient.Builder()
            .connectTimeout(10, TimeUnit.SECONDS)
            .writeTimeout(10, TimeUnit.SECONDS)
            .readTimeout(10, TimeUnit.SECONDS)
            .hostnameVerifier { _, _ -> true } /* Bypasses hostname verification (insecure for production) */
            .build()

        /* Create a POST request targeting the Flask server's /detect endpoint */
        val request = Request.Builder()
            .url("http://${ip}:5000/detect") /* Update this URL if testing on a real Android device */
            .post(requestBody)
            .build()

        Log.d("UploadToFlask", "Sending request to Flask server")

        /* Execute the request and get the response */
        val response = client.newCall(request).execute()

        Log.d("UploadToFlask", "Received HTTP ${response.code}")

        /* Return the response body as a string and log it */
        return response.body?.string().also {
            Log.d("UploadToFlask", "Response body: $it")
        }
    }
}
