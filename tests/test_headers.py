from alxhttp.headers import content_security_policy, permissions_policy


def test_permissions_policy():
  assert permissions_policy() == ''

  assert permissions_policy(autoplay=[]) == 'autoplay=()'

  assert permissions_policy(autoplay=[], fullscreen=[]) == 'autoplay=(), fullscreen=()'

  assert permissions_policy(autoplay=['self']) == 'autoplay=(self)'

  assert permissions_policy(autoplay=['src']) == 'autoplay=(src)'

  assert permissions_policy(autoplay=['*']) == 'autoplay=(*)'

  assert permissions_policy(autoplay=['https://a.example.com']) == 'autoplay=("https://a.example.com")'


def test_csp():
  assert content_security_policy() == ''

  assert content_security_policy(default_src=['self']) == "default-src 'self'"

  assert (
    content_security_policy(
      default_src=['self'],
      script_src=[
        'self',
        'https://un-pkg.com',
        'sha256-7TblKF+IjWKavJTjUFzFm8Su2HRYXIttPzbcPZBCTwY=',
      ],
      media_src=['blob:'],
    )
    == "default-src 'self'; media-src blob:; script-src 'self' https://un-pkg.com 'sha256-7TblKF+IjWKavJTjUFzFm8Su2HRYXIttPzbcPZBCTwY='"
  )
