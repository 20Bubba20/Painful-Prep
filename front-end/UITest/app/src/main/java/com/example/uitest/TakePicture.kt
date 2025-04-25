package com.example.uitest


import android.content.ContentValues
import android.os.Build
import android.os.Bundle
import android.provider.MediaStore
import androidx.appcompat.app.AppCompatActivity
import androidx.camera.core.ImageCapture
import androidx.core.content.ContextCompat
import java.util.concurrent.ExecutorService
import java.util.concurrent.Executors
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.camera.core.Preview
import androidx.camera.core.CameraSelector
import android.util.Log
import androidx.camera.core.ImageCaptureException
import com.example.uitest.databinding.TakepicturepageBinding
import java.text.SimpleDateFormat
import java.util.Locale
import android.widget.Button
import android.content.Intent


/**
 *  This program class allows for a picture to be taken
 *  and sends the result to a server to run calculations.
 *  @author Jerron Pierro and Logan Johnson
 */
class TakePicture : AppCompatActivity() {
    private lateinit var viewBinding: TakepicturepageBinding
    private lateinit var cameraExecutor: ExecutorService
    private var imageCapture: ImageCapture? = null

    /**
     *  This function starts the "TakePicture" activity,
     *  and starts the camera on the device, if permissions are given.
     *  If no permissions are given, it prompts the user to allow camera access.
     *  @param savedInstanceState
     */
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        viewBinding = TakepicturepageBinding.inflate(layoutInflater)
        setContentView(viewBinding.root)

        /* Start Camera or ask for camera permission */
        if (MainActivity.Shared.allPermissionsGranted(this)) {
            startCamera()
        }
        else {
            val ActivityResultLauncher = registerForActivityResult(ActivityResultContracts.RequestMultiplePermissions()) {
                    permissions -> MainActivity.Shared.handlePermissionsResults(this, permissions)
            }

            while (!MainActivity.Shared.allPermissionsGranted(this)) {
                MainActivity.Shared.requestPermissions(this, ActivityResultLauncher)
            }
            startCamera()
        }
        /* On the button press run takepicture() */
        viewBinding.imageCaptureButton.setOnClickListener{ takePicture() }

        cameraExecutor = Executors.newSingleThreadExecutor()

        /* Assign Buttons values */
        val toHome: Button = findViewById(R.id.index)

        /* On the button press, jump to MainActivity.kt */
        toHome.setOnClickListener {
            val intent: Intent = Intent(this, MainActivity::class.java)
            startActivity(intent)
        }
    }

    /**
     * This function is responsible for saving a photo taken within the app.
     * The photo will be saved in InternalStorage\Pictures\PainlessPrep\{date-time}.jpg.
     */
    private fun takePicture() {
        /* Get a stable reference of the modifiable image capture use case */
        val imageCapture = imageCapture ?: return

        /* Create time stamped name and MediaStore entry. */
        val name = SimpleDateFormat(MainActivity.FILENAME_FORMAT, Locale.US)
            .format(System.currentTimeMillis())

        /* Set value types to be used when saving a photo */
        val contentValues = ContentValues().apply {
            put(MediaStore.MediaColumns.DISPLAY_NAME, name)
            put(MediaStore.MediaColumns.MIME_TYPE, "image/jpeg")
            if(Build.VERSION.SDK_INT > Build.VERSION_CODES.P) {
                put(MediaStore.Images.Media.RELATIVE_PATH, getString(R.string.SaveDirectory))
            }
        }

        /* Create output options object which contains file + metadata */
        val outputOptions = ImageCapture.OutputFileOptions
            .Builder(contentResolver,
                MediaStore.Images.Media.EXTERNAL_CONTENT_URI,
                contentValues)
            .build()

        /* Set up image capture listener, which is triggered after photo has been taken */
        imageCapture.takePicture(
            outputOptions,
            ContextCompat.getMainExecutor(this),
            object : ImageCapture.OnImageSavedCallback {
                override fun onError(exc: ImageCaptureException) {
                    Log.e(MainActivity.TAG, "Photo capture failed: ${exc.message}", exc)
                }

                override fun onImageSaved(output: ImageCapture.OutputFileResults) {
                    val savedUri = output.savedUri
                    val msg = "Photo capture succeeded: $savedUri"
                    Toast.makeText(baseContext, msg, Toast.LENGTH_SHORT).show()
                    Log.d(MainActivity.TAG, msg)

                    /* If the photoURI returns something jump to Dimensions.kt */
                    val intent: Intent = Intent(applicationContext, Dimensions::class.java)
                    intent.putExtra("photo", output.savedUri)
                    startActivity(intent)
                }
            }
        )
    }

    /**
     * This function starts the camera.
     */
    private fun startCamera() {
        val cameraProviderFuture = ProcessCameraProvider.getInstance(this)

        cameraProviderFuture.addListener(Runnable {
            val cameraProvider: ProcessCameraProvider = cameraProviderFuture.get()

            val preview = Preview.Builder().build().also {
                it.setSurfaceProvider(viewBinding.viewFinder.surfaceProvider)
            }
            imageCapture = ImageCapture.Builder().build()

            val cameraSelector = CameraSelector.DEFAULT_BACK_CAMERA
            try {
                cameraProvider.unbindAll()

                cameraProvider.bindToLifecycle(this, cameraSelector, preview, imageCapture)
            }
            catch (exc: Exception) {
                Log.e(MainActivity.TAG, "Use case binding failed", exc)
            }
        }, ContextCompat.getMainExecutor(this))
    }

    /**
     * This function destroys the current camera object.
     */
    override fun onDestroy() {
        super.onDestroy()
        cameraExecutor.shutdown()
    }
}
