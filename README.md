# ABP anti-circumvention filter list

Adblock Plus (ABP) filter list to fight "circumvention ads."
 
## Introduction

Some providers have begun to show ads that are harder to detect for ad-blocking tools like ABP, thus tricking ad-blocker users into downloading and displaying unrequested and intrusive advertising ("circumvention ads").

This filter list is drafted and maintained by ABP and is intended to detect and block circumvention ads.

The ABP anti-circumvention filter list is a supplementary list; it's not related or operated by the EasyList community and it doesn't replace EasyList filters or any other language-specific list.

## Installation

[**ABP Anti-Circumvention Filter List**](https://easylist-downloads.adblockplus.org/abp-filters-anti-cv.txt) is enabled by default in [Adblock Plus](https://adblockplus.org/) version 3.1 or higher.

## Authors

* [**arsykan**](https://github.com/arsykan)
* [**mile-ne**](https://github.com/mile-ne)
* [**monzta**](https://github.com/monzta)
* [**wizmak**](https://github.com/wizmak)


See also the full list of [contributors](https://github.com/abp-filters/abp-filters-anti-cv/graphs/contributors).

## Ubuntu helper script

This repository ships with a small utility that prepares consolidated
advertising and tracking block lists that can be imported into `/etc/hosts`,
`dnsmasq`, or any other tool that accepts bare domain lists.

```
python3 tools/adblock_privacy_guard.py --output ~/blocklist.hosts
```

By default the script merges EasyList, EasyPrivacy, and the StevenBlack hosts
project. The resulting file begins with metadata comments and a sorted list of
blocked domains that can be copied directly into your preferred blocker. The
command-line interface supports switching the output format to `dnsmasq` or a
plain `domains` list, adding extra URLs, and appending individual domains via
`--extra-domain`.

### طريقة التثبيت والاستخدام على أوبونتو

1. **تنزيل المستودع**

   ```bash
   git clone https://github.com/abp-filters/abp-filters-anti-cv.git
   cd abp-filters-anti-cv
   ```

2. **تشغيل الأداة وإنشاء ملف الحظر**

   ```bash
   python3 tools/adblock_privacy_guard.py --output ~/blocklist.hosts
   ```

   يمكنك تغيير اسم الملف أو مساره بحسب احتياجك، كما يمكن تغيير الصيغة إلى
   `dnsmasq` أو `domains` باستخدام الخيار `--format`.

3. **أخذ نسخة احتياطية من ملف النظام (اختياري ولكن مستحسن)**

   ```bash
   sudo cp /etc/hosts /etc/hosts.backup.$(date +%Y%m%d)
   ```

4. **دمج قائمة الحظر مع ملف hosts**

   ```bash
   sudo sh -c 'cat ~/blocklist.hosts >> /etc/hosts'
   ```

   إذا كنت تستخدم `dnsmasq` بدلًا من ملف `hosts`، انسخ المخرجات إلى ملف مثل
   `/etc/dnsmasq.d/adblock.conf` ثم أعد تشغيل الخدمة باستخدام
   `sudo systemctl restart dnsmasq`.

5. **تحديث القائمة مستقبلًا**

   أعد تشغيل الأمر في الخطوة (2) كلما رغبت بتحديث القوائم، ثم كرر خطوة الدمج أو
   استبدل الملف المخصص لديك.

## License

This project is free, open source, and licensed under GPLv3. See [LICENSE](https://github.com/abp-filters/abp-filters-anti-cv/blob/master/LICENSE) for details. 

## Contributing

Please see our [Contribution page](https://github.com/abp-filters/abp-filters-anti-cv/blob/master/CONTRIBUTING.md) for information on how to report issues to us.
