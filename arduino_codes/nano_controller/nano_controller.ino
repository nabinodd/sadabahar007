#include "DHT.h"
#define DHTTYPE DHT11

const int dht_pin = A1;
const int mq135_pin = A0;
const int res_flup_pin = 12;
const int res_fldwn_pin = 11;
const int humifr_relay1_pin = 2;
const int humifr_relay2_pin = 3;

int mq135_corr_factor = 4;

float co2 = 0;
float tmpr = 0;
float humi = 0;

int looping_delay = 100;
int max_mq135_count = 25, mq135_count = 0;
int max_dht_count = 10, dht_count = 0;
int max_flsw_sample_count = 10, flsw_sample_count = 0;

float mq135_sum = 0;
float humi_sum = 0, tmpr_sum = 0;

int res_flup_on_count = 0;
int res_fldwn_on_count = 0;
bool res_flup_on_sts = false;
bool res_fldwn_on_sts = false;

bool humifr_relay1_sts = false;
bool humifr_relay2_sts = false;
bool humifr_relay1_set = false;
bool humifr_relay2_set = false;

DHT dht(dht_pin, DHTTYPE);

void setup()
{
   pinMode(res_flup_pin, INPUT_PULLUP);
   pinMode(res_fldwn_pin, INPUT_PULLUP);

   pinMode(humifr_relay1_pin, OUTPUT);
   pinMode(humifr_relay2_pin, OUTPUT);

   Serial.begin(9600);
   dht.begin();
}

bool updateMq135()
{
   int aval = analogRead(mq135_pin);
   mq135_sum = mq135_sum + aval;
   mq135_count++;
   if (mq135_count >= max_mq135_count)
   {
      co2 = (mq135_sum / mq135_count) * mq135_corr_factor;
      mq135_count = 0;
      mq135_sum = 0;
      return true;
   }
   else
      return false;
}

bool updateDht()
{
   float humi_rd = dht.readHumidity();
   float tmpr_rd = dht.readTemperature();

   humi_sum = humi_sum + humi_rd;
   tmpr_sum = tmpr_sum + tmpr_rd;
   dht_count++;
   if (dht_count >= max_dht_count)
   {
      humi = humi_sum / dht_count;
      tmpr = tmpr_sum / dht_count;
      dht_count = 0;
      humi_sum = 0;
      tmpr_sum = 0;
      return true;
   }
   else
      return false;
}

bool updateFlsw()
{
   bool fl_up = !digitalRead(res_flup_pin);
   bool fl_dwn = !digitalRead(res_fldwn_pin);
   if (fl_up)
      res_flup_on_count++;
   else
      res_flup_on_count--;
   if (fl_dwn)
      res_fldwn_on_count++;
   else
      res_fldwn_on_count--;
   flsw_sample_count++;
   if (flsw_sample_count >= max_flsw_sample_count)
   {
      if (res_flup_on_count > 0)
         res_flup_on_sts = true;
      else if (res_flup_on_count < 0)
         res_flup_on_sts = false;
      else
         ;
      // Serial.println("res_flup_sts UNCHANGED");

      if (res_fldwn_on_count > 0)
         res_fldwn_on_sts = true;
      else if (res_fldwn_on_count < 0)
         res_fldwn_on_sts = false;
      else
         ;
      // Serial.println("res_fldwn_sts UNCHANGED");

      res_flup_on_count = 0;
      res_fldwn_on_count = 0;
      flsw_sample_count = 0;
      return true;
   }
   else
      return false;
}

void setRelay(bool re1, bool re2)
{
   digitalWrite(humifr_relay1_pin, re1);
   humifr_relay1_sts = re1;
   digitalWrite(humifr_relay2_pin, re2);
   humifr_relay2_sts = re2;
}

void loop()
{
   if (Serial.available() > 0)
   {
      int cmd = Serial.parseInt();
      if (cmd != 0)
      {
         // Serial.print("CMD RX : ");
         // Serial.println(cmd);
         if (cmd == 1)
            Serial.println(String(res_flup_on_sts) + "," + String(res_fldwn_on_sts));
         else if (cmd == 2)
            Serial.println(String(humifr_relay1_sts) + "," + String(humifr_relay2_sts));
         else if (cmd == 3)
            Serial.println(String(co2) + "," + String(tmpr) + "," + String(humi));
         else if (cmd == 4)
            setRelay(true, true);
         else if (cmd == 5)
            setRelay(false, false);
      }
   }
   if (updateDht())
   {
      // Serial.print(F("Humidity: "));
      // Serial.print(humi);
      // Serial.print(F("%  Temperature: "));
      // Serial.print(tmpr);
      // Serial.println(F("°C "));
   }
   if (updateMq135())
   {
      // Serial.print("co2 : ");
      // Serial.println(co2);
   }
   if (updateFlsw())
   {
      // Serial.print("res_flup_on_sts : ");
      // Serial.print(res_flup_on_sts);
      // Serial.print("\tres_fldwn_on_sts : ");
      // Serial.println(res_fldwn_on_sts);
   }
   delay(looping_delay);
}