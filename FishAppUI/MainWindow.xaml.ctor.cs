namespace FishAppUI;

partial class MainWindow
{
    public MainWindow()
    {
        InitializeComponent();
        InitializeButtonStates();



        // File menu
        FileNewMenuItem.Click += FileNew_Click;
        FileOpenMenuItem.Click += FileOpen_Click;
        FileSaveMenuItem.Click += FileSave_Click;
        FileSaveAsMenuItem.Click += FileSaveAs_Click;
        //UndoMenuItem.Click += UndoMenuItem_Click; //##
        //ResetMenuItem.Click += ResetMenuItem_Click; //##
        FilePropertiesMenuItem.Click += FileProperties_Click;
        FileQuitMenuItem.Click += FileQuit_Click;


        // Clipboard menu
        ClipboardCopyMenuItem.Click += ClipboardCopy_Click;
        ClipboardPasteMenuItem.Click += ClipboardPaste_Click;
        ClipboardCutMenuItem.Click += ClipboardCut_Click;


        // Image menu
        RectangularSelectMenuItem.Click += ImageRectangularSelect_Click;
        FreeformSelectMenuItem.Click += ImageFreeformSelect_Click;
        PolygonSelectMenuItem.Click += ImagePolygonSelect_Click;
        CropMenuItem.Click += ImageCrop_Click;
        ResizeMenuItem.Click += ImageResize_Click;
        Rotate90MenuItem.Click += Rotate90Button_Click;
        Rotate180MenuItem.Click += Rotate180Button_Click;
        Rotate270MenuItem.Click += Rotate270Button_Click;
        FlipHorizontalMenuItem.Click += FlipHorizontal_Click;
        FlipVerticalMenuItem.Click += FlipVertical_Click;


        // Tools menu
        ZoomInMenuItem.Click += ZoomIn_Click;
        ZoomOutMenuItem.Click += ZoomOut_Click;
        EraserMenuItem.Click += Eraser_Click;
        ColorPickerMenuItem.Click += ColorPicker_Click;
        BrushBasicMenuItem.Click += BrushBasic_Click;
        BrushTextureMenuItem.Click += BrushTexture_Click;
        BrushPatternMenuItem.Click += BrushPattern_Click;
        TextToolMenuItem.Click += TextTool_Click;
        GrayscaleMenuItem.Click += Grayscale_Click;
        OnnxMenuItem.Click += Onnx_Click;
        GaussianBlurMenuItem.Click += GaussianBlur_Click;
        SobelFilterMenuItem.Click += SobelFilter_Click;
        BinaryFilterMenuItem.Click += BinaryFilter_Click;


        // Shapes menu
        ShapeRectangleMenuItem.Click += ShapeRectangle_Click;
        ShapeEllipseMenuItem.Click += ShapeEllipse_Click;
        ShapeLineMenuItem.Click += ShapeLine_Click;
        ShapePolygonMenuItem.Click += ShapePolygon_Click;
        ShapeOutlineColorMenuItem.Click += ShapeOutlineColor_Click;
        ShapeFillColorMenuItem.Click += ShapeFillColor_Click;


        // Color menu
        ColorPaletteMenuItem.Click += ColorPalette_Click;
        BrushSizeSmallMenuItem.Click += BrushSizeSmall_Click;
        BrushSizeMediumMenuItem.Click += BrushSizeMedium_Click;
        BrushSizeLargeMenuItem.Click += BrushSizeLarge_Click;

    }
}
