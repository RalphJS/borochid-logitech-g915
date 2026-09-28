# borochid-logitech-g915

[Borochid](https://github.com/RalphJS/borochid) device package for the
**Logitech G915 LIGHTSPEED** keyboard (wireless, through its receiver
`046d:c541`).

Data only: the key map (position, per-key lighting zone and HID usage of
every key), the G-keys, three M-key subprofiles, the starting settings and
the settings UI. The code is
[`borochid-driver-logitech-keyboard`](https://github.com/RalphJS/borochid-driver-logitech-keyboard),
which Borochid offers to install through the system package manager, and
which brings the HID++ broker the keyboard needs (see its README for why).

## What you get

Per Borochid profile, and per M1-M3 subprofile where noted:

* G1-G5 bindings (subprofile)
* lighting: per-key colours, breathing, colour cycle, wave, ripple, off
  (subprofile)
* keys the game-mode key disables (both Super keys are always disabled
  by the keyboard)
* brightness and report rate

MR does nothing. Nothing is ever written to the keyboard's memory.

## The key map

`tools/make_layout.py` writes the manifest's `keyboard` section (US ANSI
layout, 122 keys, 114 with lights) from tables that are easier to check
than the JSON. Run it after changing them:

```sh
python3 tools/make_layout.py logitech.g915/manifest.json
```

## Checking and publishing

```sh
make check                              # schema + key map validation
make install-local                      # use it here without a registry
make publish REGISTRY=../registry-out KEY=publisher.key
```

## License

Apache 2.0, except the picture; see NOTICE.
