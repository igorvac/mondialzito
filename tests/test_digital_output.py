from unittest.mock import MagicMock, patch


@patch("src.digital.output.GPIO")
def test_on_sets_high(mock_gpio):
    from src.digital.output import DigitalOutput

    out = DigitalOutput(pin=17)
    out.on()
    mock_gpio.output.assert_called_with(17, mock_gpio.HIGH)


@patch("src.digital.output.GPIO")
def test_off_sets_low(mock_gpio):
    from src.digital.output import DigitalOutput

    out = DigitalOutput(pin=17)
    out.off()
    mock_gpio.output.assert_called_with(17, mock_gpio.LOW)
