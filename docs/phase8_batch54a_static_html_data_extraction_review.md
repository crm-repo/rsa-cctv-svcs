# Batch 54A Static HTML Data Extraction Review

This package contains reviewable JSON generated from the uploaded legacy static HTML files. It does not modify DynamoDB.

## Important extraction rules

- products.html is the master source for product records; duplicate product cards in promotions.html, brands.html, and index.html are intentionally ignored.
- index.html homepage package, featured product, promo, brand, and service preview cards are not inserted as separate/duplicate records; they should reference main products/brands/services tables by query conditions.
- Image paths are preserved as relative object keys by stripping only the leading ./ from legacy HTML paths.
- Sale products use price = regular/old price and sale_price = sale/current price. No old_price field is introduced.
- Categories include a subcategories array. Products include subcategory_key and subcategory.
- No DynamoDB tables should be deleted during import. Records can be wiped/reseeded after review, while rsa_id_counters must not be reset downward.

## Record counts

- categories: 7
- brands: 22
- products: 28
- key_features: 188
- about: 1
- project_gallery: 4
- services: 12
- contact_us: 10
- customers: 0
- bookings: 0
- inquiries: 0

## Categories and subcategories

| Category | Key | Prefix | Subcategories |
|---|---|---|---|
| CCTV Cameras | cctv | CCTV | 6MP Bullet Camera, 2MP Dome Camera, 2MP Turret Camera, 2MP Bullet Camera, 8MP Bullet Camera, 8MP Turret Camera, Analog Dome Camera, Smart IP Camera |
| Recorders | recorders | RECO | 4 Channel DVR, 32 Channel NVR |
| Networking | networking | NETW | 16-Port Switch, 48-Port Switch, 24-Port Switch |
| Accessories | accessories | ACCS | Camera Cable |
| Power Supply | power | POWR | 12V Power Supply |
| Storage | storage | STOR | Surveillance HDD, Storage |
| Packages/Kits | packages | PACK | Camera Kit, Camera Kits |

## Product review list

| # | Product ID | Product | Category | Subcategory | Brand | Price | Sale Price | Image |
|---:|---|---|---|---|---|---:|---:|---|
| 1 | CCTV-0000001 | Hikvision 6 MP AcuSense Fixed Bullet Network Camera | CCTV Cameras | 6MP Bullet Camera | Hikvision | 2950.0 |  | assets/images/products/bullet-camera-01.png |
| 2 | CCTV-0000002 | Dahua 2MP 4x PTZ HDCVI Camera | CCTV Cameras | 2MP Dome Camera | Dahua | 3200.0 | 2750.0 | assets/images/products/dome-camera-01.png |
| 3 | CCTV-0000003 | Hikvision 2MP eco Platinum HD-TVI Turret Camera | CCTV Cameras | 2MP Turret Camera | Hikvision | 2650.0 |  | assets/images/products/turret-camera-01.png |
| 4 | CCTV-0000004 | Axis Outdoor 2MP Varifocal Bullet Security Camera | CCTV Cameras | 2MP Bullet Camera | Axis Communications | 4500.0 | 3950.0 | assets/images/products/bullet-camera-02.png |
| 5 | RECO-0000001 | Hikvision 4-ch 1080p 1U H.265 DVR | Recorders | 4 Channel DVR | Hikvision | 3950.0 |  | assets/images/products/8ch-dvr-02.png |
| 6 | CCTV-0000005 | Hikvision 2 MP Fixed Dome Network Camera | CCTV Cameras | 2MP Dome Camera | Hikvision | 1900.0 |  | assets/images/products/dome-camera-02.png |
| 7 | NETW-0000001 | D-Link 16-Port Gigabit Smart Managed Switch | Networking | 16-Port Switch | D-Link | 2800.0 | 2350.0 | assets/images/products/switch-02.png |
| 8 | RECO-0000002 | Uniview 32 Channel 4SATA Ultra 265 Network Video Recorder | Recorders | 32 Channel NVR | Uniview | 14500.0 |  | assets/images/products/8ch-dvr-04.png |
| 9 | CCTV-0000006 | Dahua 8MP 4K Smart Dual Light HDCVI Motorized Vari-Focal Bullet Camera | CCTV Cameras | 8MP Bullet Camera | Dahua | 4500.0 | 3950.0 | assets/images/products/bullet-camera-05.png |
| 10 | CCTV-0000007 | Hikvision 4K WDR Fixed Turret Network Camera with Build-in Mic | CCTV Cameras | 8MP Turret Camera | Hikvision | 2650.0 |  | assets/images/products/turret-camera-02.png |
| 11 | NETW-0000002 | Cisco 48-port Gigabit PoE Stackable Switch | Networking | 48-Port Switch | Cisco | 7000.0 | 6750.0 | assets/images/products/switch-01.png |
| 12 | CCTV-0000008 | Panasonic Day/Night Fixed Dome Camera with IR LED | CCTV Cameras | Analog Dome Camera | Panasonic | 1100.0 |  | assets/images/products/dome-camera-03.png |
| 13 | RECO-0000003 | Hikvision 4-CH 3MP 1U Turbo HD DVR | Recorders | 4 Channel DVR | Hikvision | 1500.0 |  | assets/images/products/8ch-dvr-01.png |
| 14 | CCTV-0000009 | Hikvision 2MP Fixed Turret Camera | CCTV Cameras | 2MP Turret Camera | Hikvision | 2650.0 |  | assets/images/products/turret-camera-03.png |
| 15 | NETW-0000003 | Cisco 24-Port Gigabit Stackable Managed Switch | Networking | 24-Port Switch | Cisco | 2800.0 | 2350.0 | assets/images/products/switch-03.png |
| 16 | STOR-0000001 | Seagate 2TB SkyHawk HDD | Storage | Surveillance HDD | Seagate | 2350.0 |  | assets/images/products/storage-01.png |
| 17 | CCTV-0000010 | IMOU Pan Tilt Smart IP Camera White | CCTV Cameras | Smart IP Camera | Imou | 2990.0 |  | assets/images/products/ipcam-01.png |
| 18 | RECO-0000004 | Uniview AI IQ 4K 32 Channel 16 PoE NVR | Recorders | 32 Channel NVR | Uniview | 5550.0 |  | assets/images/products/nvr-02.png |
| 19 | PACK-0000001 | Dahua CCTV Camera Solution-4 CAM Package | Packages/Kits | Camera Kit | Dahua | 8500.0 | 7250.0 | assets/images/products/package-01.png |
| 20 | ACCS-0000001 | AXIS F7308 Cable Black 8m | Accessories | Camera Cable | Axis Communications | 950.0 |  | assets/images/products/cable-01.png |
| 21 | CCTV-0000011 | AVTech 2MP Motorized Varifocal Lens Bullet IP Camera | CCTV Cameras | 2MP Bullet Camera | AVTech | 2000.0 | 1650.0 | assets/images/products/bullet-camera-04.png |
| 22 | CCTV-0000012 | Ezviz Wi-Fi Smart Home Camera | CCTV Cameras | 2MP Bullet Camera | EZVIZ | 3550.0 |  | assets/images/products/outdoor-01.png |
| 23 | STOR-0000002 | Seagate 1TB SkyHawk HDD | Storage | Storage | Seagate | 1850.0 |  | assets/images/products/storage-02.png |
| 24 | POWR-0000001 | Hanwha PWR-12DC-8-5 8 Camera 12VDC 5Amp Power Supply | Power Supply | 12V Power Supply | Hanwha | 2250.0 |  | assets/images/products/powersupply-01.png |
| 25 | PACK-0000002 | Dahua HD-CVI 1080P CCTV Camera Package | Packages/Kits | Camera Kits | Dahua |  |  | assets/images/products/package-dahua-01.png |
| 26 | PACK-0000003 | Dahua 6MP IP CCTV Camera System with Built-in Mic | Packages/Kits | Camera Kits | Dahua |  |  | assets/images/products/package-dahua-02.png |
| 27 | PACK-0000004 | Hikvision 4MP HD IP CCTV Camera System | Packages/Kits | Camera Kits | Hikvision |  |  | assets/images/products/package-hikvision-01.png |
| 28 | PACK-0000005 | Hikvision 2-Way Audio HD IP CCTV Camera Package | Packages/Kits | Camera Kits | Hikvision |  |  | assets/images/products/package-hikvision-02.png |

## Next step
Review these JSON files. After approval, Batch 54B can add a safe wipe/reseed import script that keeps DynamoDB tables and does not reset id counters downward.
