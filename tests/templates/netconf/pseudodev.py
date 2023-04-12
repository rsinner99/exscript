commands = (
    (
'''
<rpc>
    <get xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
        <filter>abc</filter>
    </get>
</rpc>
'''
, 
'<data>abc</data>'),
)
