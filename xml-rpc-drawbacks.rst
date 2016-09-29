======================
 Drawbacks of XML-RPC
======================

In my presentation, I note that XML-RPC has many problems that make
REST superior, but I don't have time to go into all of them. I talk
about a few of the most important ones, largely from a viewpoint of
how REST works.

One of the major issues is that XML-RPC routes all requests to the
same URL. This keeps routing easy, but it means that you lose a lot of
the power of HTTP. You can't use HTTP authentication, for instance,
unless your entire application uses a flat authorization scheme. With
REST, each operation uses a separate URL and verb combination, so HTTP
authentication and authorization is often enough for many simple
applications.

Similarly, that makes it harder to gather statistics on your
application. With a well-written REST app, you can find all sorts of
performance metrics just by looking at your httpd logs.

That also makes it harder to split XML-RPC applications into
microservices. If a REST app starts to scale poorly in a particular
direction, you can very easily split a portion of it off into its own
application and route those requests to a completely different set of
servers. No such luck with XML-RPC.

Ultimately, with XML-RPC, you'd have to do layer 7 inspection to get
basically any information about what the application is doing. (Or,
more likely, build it into the application itself.) This might be an
acceptable approach for large applications that are extensively
planned beforehand, but it's terrible for smaller services and organic
growth.

Additionally, XML encoding is expensive. XML requires escaping lots
and lots of characters, so encoding every request (and, moreover,
every response) in XML can greatly increase bandwidth
requirements. This is particularly true if you are dealing with XML
data (escape ALL THE THINGS!) or binary data, which must be
base64-encoded. And XML-RPC is a particularly verbose form of XML, to
boot. JSON is much more lightweight, and REST can easily handle
different content types for binary (or other) data.
