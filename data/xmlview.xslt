<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="2.0"
xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:strip-space elements="*" />
<xsl:output method="html" version="2.0" encoding="UTF-8" indent="no"/>

    <xsl:template match="/">
      <html>
      <head>
        <style type="text/css">
           .node { font-weight: normal }
           .nodeName { font-weight: normal }
           .nodeLine { font-weight: bold }
        </style>
      </head>
      <body>
      <h2>Transformed XML</h2>
      <xsl:apply-templates select="/*"/>
      </body>
      </html>
    </xsl:template>

    <xsl:template match="node()">
        <xsl:param name="level" select="0"/>
        <div>
            <xsl:attribute name="style">
                 <xsl:value-of select="concat('margin-left: ',$level,'em')"/>
            </xsl:attribute>
            <span class="nodeLine">&lt;<span class="nodeName"><xsl:value-of select="name(.)"/></span>
                <xsl:for-each select="@*"><xsl:value-of select="concat(' ',name(.))"/>="<xsl:value-of select="."/>"</xsl:for-each>&gt;<xsl:value-of select="text()"/><xsl:apply-templates select="*"><xsl:with-param name="level" select="2"/></xsl:apply-templates><span class="node">&lt;/<span class="nodeName"><xsl:value-of select="name(.)"/></span>&gt;</span></span>
        </div> 
    </xsl:template>
</xsl:stylesheet>