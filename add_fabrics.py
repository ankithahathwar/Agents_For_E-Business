import json

with open("products.json", "r") as f:
    products = json.load(f)

fabric_entries = [
    # ── PREMIUM SUITING FABRICS ──────────────────────────────────────────
    {
        "base_product_id": "fabric_merino_wool_140s",
        "name": "Super 140s Australian Merino Wool",
        "category": "Bespoke Fabrics",
        "description": "Raw high-grade structural suiting wool sold independently by the linear meter. Smooth, crease-resistant with a crisp drape. Ideal for year-round corporate suiting. Weight: 280g/m. Use: Premium Suiting.",
        "customization_matrix": {
            "use_case": "Premium Suiting Options",
            "weight_gsm": "280g/m",
            "weave_texture": "Smooth, crease-resistant with a crisp drape",
            "best_for": "Year-round corporate suiting",
            "price_per_meter": 45.00,
            "min_cut_length_meters": 3,
            "unit_price_at_min_cut": 135.00
        }
    },
    {
        "base_product_id": "fabric_irish_linen",
        "name": "Pure Irish Flamed Linen",
        "category": "Bespoke Fabrics",
        "description": "Premium summer suiting linen sold independently by the linear meter. Slubby, airy, open-weave structure. Best suited for destination and warm-weather styling. Weight: 210g/m. Use: Premium Suiting.",
        "customization_matrix": {
            "use_case": "Premium Suiting Options",
            "weight_gsm": "210g/m",
            "weave_texture": "Slubby, airy, open-weave structure",
            "best_for": "Summer destination styling",
            "price_per_meter": 45.00,
            "min_cut_length_meters": 3,
            "unit_price_at_min_cut": 135.00
        }
    },
    {
        "base_product_id": "fabric_zegna_silk_wool",
        "name": "Ermenegildo Zegna Silk-Wool Blend",
        "category": "Bespoke Fabrics",
        "description": "Luxury Italian silk-wool blend sold independently by the linear meter. Subtle luxury sheen with an immaculate hang. Designed for high-profile gala suiting. Weight: 240g/m. Use: Premium Suiting.",
        "customization_matrix": {
            "use_case": "Premium Suiting Options",
            "weight_gsm": "240g/m",
            "weave_texture": "Subtle luxury sheen with an immaculate hang",
            "best_for": "High-profile galas and black-tie events",
            "price_per_meter": 45.00,
            "min_cut_length_meters": 3,
            "unit_price_at_min_cut": 135.00
        }
    },

    # ── BRIDAL & EVENING GOWN FABRICS ───────────────────────────────────
    {
        "base_product_id": "fabric_maison_silk_satin",
        "name": "Maison Lyon Heavy Silk Satin",
        "category": "Bespoke Fabrics",
        "description": "Ultra-luxe French bridal silk satin sold independently by the linear meter. Ultra-rich luster with structural body. The gold standard for bridal gown construction. Weight: 320g/m. Use: Bridal & Evening Gowns.",
        "customization_matrix": {
            "use_case": "Bridal & Evening Gown Outfits",
            "weight_gsm": "320g/m",
            "weave_texture": "Ultra-rich luster with structural body",
            "best_for": "Bridal gowns and red-carpet evening wear",
            "price_per_meter": 45.00,
            "min_cut_length_meters": 3,
            "unit_price_at_min_cut": 135.00
        }
    },
    {
        "base_product_id": "fabric_chantilly_lace",
        "name": "French Chantilly Corded Lace",
        "category": "Bespoke Fabrics",
        "description": "Delicate French corded lace sold independently by the linear meter. Sheer floral relief overlays with fine bobbin-lace detailing. For bridal overlays and evening bodices. Weight: 110g/m. Use: Bridal & Evening Gowns.",
        "customization_matrix": {
            "use_case": "Bridal & Evening Gown Outfits",
            "weight_gsm": "110g/m",
            "weave_texture": "Delicate, sheer floral relief overlays",
            "best_for": "Bridal overlays, bodice detailing, and evening gowns",
            "price_per_meter": 45.00,
            "min_cut_length_meters": 3,
            "unit_price_at_min_cut": 135.00
        }
    },
    {
        "base_product_id": "fabric_italian_chiffon",
        "name": "Italian Silk Chiffon",
        "category": "Bespoke Fabrics",
        "description": "Featherweight Italian silk chiffon sold independently by the linear meter. Translucent fluid weave for ethereal draping. Ideal for gown overlays and flowing sleeves. Weight: 80g/m. Use: Bridal & Evening Gowns.",
        "customization_matrix": {
            "use_case": "Bridal & Evening Gown Outfits",
            "weight_gsm": "80g/m",
            "weave_texture": "Feather-light, translucent fluid weave",
            "best_for": "Gown overlays, sleeves, and flowing drape elements",
            "price_per_meter": 45.00,
            "min_cut_length_meters": 3,
            "unit_price_at_min_cut": 135.00
        }
    },

    # ── TRADITIONAL WEDDING & FESTIVE SAREE FABRICS ──────────────────────
    {
        "base_product_id": "fabric_kanchipuram_silk",
        "name": "Pure Kanchipuram Handwoven Silk",
        "category": "Bespoke Fabrics",
        "description": "Authentic South Indian Kanchipuram handwoven silk sold independently by the meter. Thick silk yarn dipped in pure silver-dipped gold zari. The definitive fabric for bridal and festive sarees. Weight: 450g. Use: Traditional Wedding & Festive Sarees.",
        "customization_matrix": {
            "use_case": "Traditional Wedding & Festive Sarees",
            "weight_gsm": "450g",
            "weave_texture": "Thick silk yarn dipped in pure silver-dipped gold zari",
            "best_for": "Bridal sarees, temple festive wear, and grand wedding occasions",
            "price_per_meter": 45.00,
            "min_cut_length_meters": 3,
            "unit_price_at_min_cut": 135.00
        }
    },
    {
        "base_product_id": "fabric_banarasi_georgette",
        "name": "Varanasi Banarasi Georgette",
        "category": "Bespoke Fabrics",
        "description": "Traditional Varanasi Banarasi georgette sold independently by the meter. Soft crinkle texture interwoven with delicate floral bootis. The heritage choice for festive saree draping. Weight: 310g. Use: Traditional Wedding & Festive Sarees.",
        "customization_matrix": {
            "use_case": "Traditional Wedding & Festive Sarees",
            "weight_gsm": "310g",
            "weave_texture": "Soft crinkle texture interwoven with delicate floral bootis",
            "best_for": "Festive sarees, receptions, and celebratory occasions",
            "price_per_meter": 45.00,
            "min_cut_length_meters": 3,
            "unit_price_at_min_cut": 135.00
        }
    },
    {
        "base_product_id": "fabric_tussar_matka_silk",
        "name": "Premium Tussar Matka Silk",
        "category": "Bespoke Fabrics",
        "description": "Raw-textured Tussar Matka silk sold independently by the meter. Coarse, organic matte texture with a rich natural look. Beloved for its earthy, artisanal character in saree weaving. Weight: 260g. Use: Traditional Wedding & Festive Sarees.",
        "customization_matrix": {
            "use_case": "Traditional Wedding & Festive Sarees",
            "weight_gsm": "260g",
            "weave_texture": "Coarse, organic matte texture with a rich natural look",
            "best_for": "Artistic sarees, ethnic fusion, and daytime festive occasions",
            "price_per_meter": 45.00,
            "min_cut_length_meters": 3,
            "unit_price_at_min_cut": 135.00
        }
    },

    # ── PREMIUM FABRIC SWATCH OUTFITS ────────────────────────────────────
    {
        "base_product_id": "fabric_mongolian_cashmere",
        "name": "Grade-A Mongolian Brushed Cashmere",
        "category": "Bespoke Fabrics",
        "description": "Ultra-premium Mongolian brushed cashmere sold independently by the linear meter. Plush, insulating loft with a soft cloud hand feel. The pinnacle of cold-weather luxury fabric. Weight: 480g/m. Use: Premium Fabric Swatch Outfits.",
        "customization_matrix": {
            "use_case": "Premium Fabric Swatch Outfits",
            "weight_gsm": "480g/m",
            "weave_texture": "Plush, insulating loft with a soft cloud hand feel",
            "best_for": "Winter coats, luxury overcoats, and bespoke cold-weather garments",
            "price_per_meter": 45.00,
            "min_cut_length_meters": 3,
            "unit_price_at_min_cut": 135.00
        }
    },
    {
        "base_product_id": "fabric_harris_tweed",
        "name": "Harris Tweed Handwoven Virgin Wool",
        "category": "Bespoke Fabrics",
        "description": "Certified Harris Tweed handwoven virgin wool sold independently by the linear meter. Highly durable, wind-resistant rustic herringbone weave. Authentically produced in the Outer Hebrides of Scotland. Weight: 520g/m. Use: Premium Fabric Swatch Outfits.",
        "customization_matrix": {
            "use_case": "Premium Fabric Swatch Outfits",
            "weight_gsm": "520g/m",
            "weave_texture": "Highly durable, wind-resistant rustic herringbone weave",
            "best_for": "Country jackets, structured coats, and heritage outerwear",
            "price_per_meter": 45.00,
            "min_cut_length_meters": 3,
            "unit_price_at_min_cut": 135.00
        }
    },
    {
        "base_product_id": "fabric_mulberry_twill_silk",
        "name": "Pure Mulberry Twill Silk",
        "category": "Bespoke Fabrics",
        "description": "Refined pure mulberry twill silk sold independently by the linear meter. Cool to the skin with a glossy face finish. The benchmark fabric for luxury scarves and silk garment linings. Weight: 65g. Use: Premium Fabric Swatch Outfits.",
        "customization_matrix": {
            "use_case": "Premium Fabric Swatch Outfits",
            "weight_gsm": "65g",
            "weave_texture": "Cool to the skin, glossy face finish",
            "best_for": "Luxury scarves, silk blouses, and premium garment linings",
            "price_per_meter": 45.00,
            "min_cut_length_meters": 3,
            "unit_price_at_min_cut": 135.00
        }
    },
    {
        "base_product_id": "fabric_pashmina_cashmere",
        "name": "Brushed Pashmina Cashmere Yarn",
        "category": "Bespoke Fabrics",
        "description": "Rare Himalayan brushed pashmina cashmere sold independently by the linear meter. Gossamer thin weave yet exceptionally warm. The finest natural insulating textile available. Weight: 120g. Use: Premium Fabric Swatch Outfits.",
        "customization_matrix": {
            "use_case": "Premium Fabric Swatch Outfits",
            "weight_gsm": "120g",
            "weave_texture": "Gossamer thin weave yet exceptionally warm",
            "best_for": "Ultra-lightweight luxury shawls, wraps, and bespoke accessories",
            "price_per_meter": 45.00,
            "min_cut_length_meters": 3,
            "unit_price_at_min_cut": 135.00
        }
    }
]

products.extend(fabric_entries)

with open("products.json", "w") as f:
    json.dump(products, f, indent=2)

print(f"✅ Done! Added {len(fabric_entries)} Bespoke Fabric entries.")
print(f"   Total products in file: {len(products)}")
for fe in fabric_entries:
    print(f"   + {fe['base_product_id']} | {fe['name']}")
