:banner: banners/email_gateway.jpg

==================
Eagle email gateway
==================

The Eagle mail gateway allows you to inject directly all the received emails in Eagle.

Its principle is straightforward: your SMTP server executes the "mailgate" script for every new incoming email.

The script takes care of connecting to your Eagle database through XML-RPC, and send the emails via the MailThread.message_process() feature.

Prerequisites
-------------
- Administrator access to the Eagle database.
- Your own mail server such as Postfix or Exim.
- Technical knowledge on how to configure an email server.

For Postfix
-----------
In you alias config (/etc/aliases):

.. code-block:: text

	email@address: "|/eagle-directory/addons/mail/static/scripts/eagle-mailgate.py -d <database-name> -u <userid> -p <password>"

.. note:: Resources
    - `Postfix <http://www.postfix.org/documentation.html>`
    - `Postfix aliases <http://www.postfix.org/aliases.5.html>`
    - `Postfix virtual <http://www.postfix.org/virtual.8.html>`


For Exim
--------
.. code-block:: text

	*: |/eagle-directory/addons/mail/static/scripts/eagle-mailgate.py -d <database-name> -u <userid> -p <password>

.. note:: Resources
    - `Exim <https://www.exim.org/docs.html>`


.. note:: If you don't have access/manage your email server, use `inbound messages<https://www.eagle-erp.com/documentation/user/12.0/discuss/email_servers.html#how-to-manage-inbound-messages>`.
