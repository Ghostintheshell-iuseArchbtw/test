import socket
import threading
import logging
import unittest
from unittest.mock import patch

# Import the module containing your honeypot_func
from practice import honeypot_func

class TestHoneypotFunc(unittest.TestCase):
    def test_honeypot_func(self):
        # Mock the socket and logger
        mock_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        mock_logger = logging.getLogger()

        # Mock the bind and listen methods of the socket
        with patch('socket.socket') as mock_socket_class:
            mock_socket_class.return_value = mock_socket
            mock_socket.bind.return_value = None
            mock_socket.listen.return_value = None

            # Mock the accept method of the socket
            with patch.object(mock_socket, 'accept') as mock_accept:
                # Mock the log_func and threading.Thread
                with patch('practice.log_func') as mock_log_func, \
                        patch('practice.threading.Thread') as mock_thread:
                    # Set up the expected values
                    port = 1234
                    log_file_path = '/path/to/log/file'

                    # Call the honeypot_func
                    honeypot_func(mock_socket, port, log_file_path)

                    # Assert that the bind and listen methods were called
                    mock_socket.bind.assert_called_once_with(('', port))
                    mock_socket.listen.assert_called_once_with(5)

                    # Assert that the accept method was called
                    mock_accept.assert_called_once()

                    # Assert that the log_func was called with the correct arguments
                    mock_log_func.assert_called_once_with(log_file_path, mock_accept.return_value[1])

                    # Assert that the connection was closed
                    mock_accept.return_value[0].close.assert_called_once()

                    # Assert that the logger was called with the correct messages
                    mock_logger.info.assert_any_call(f'Honeypot {port} listening on port {port}')
                    mock_logger.info.assert_any_call(f'Honeypot {port} connection from {mock_accept.return_value[1]}')

if __name__ == '__main__':
    unittest.main()