package com.geely.monjaro

import android.app.Activity
import android.content.Context
import android.location.LocationManager
import android.os.Bundle
import android.provider.Settings

class MainActivity : Activity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableGps()
    }

    private fun enableGps() {
        try {
            Settings.Secure.putString(contentResolver, Settings.Secure.LOCATION_PROVIDERS_ALLOWED, "gps")
        } catch (e: SecurityException) {
            e.printStackTrace()
        }
    }
}
