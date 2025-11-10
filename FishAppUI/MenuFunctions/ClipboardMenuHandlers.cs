using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;

namespace FishAppUI.MenuFunctions
{
    /*
    <!-- Clipboard Menu -->
    <MenuItem Header = "_Clipboard" >
        <MenuItem Header = "Copy"   Click="ClipboardCopy_Click"/>
        <MenuItem Header = "Paste"  Click="ClipboardPaste_Click"/>
        <MenuItem Header = "Cut"    Click="ClipboardCut_Click"/>
    </MenuItem>
    */
    internal class ClipboardMenuHandlers
    {

        public readonly MainWindow _mainWindow;

        public ClipboardMenuHandlers(MainWindow mainWindow)
        {
            _mainWindow = mainWindow;
        }


        // <MenuItem Header = "Copy"   Click="ClipboardCopy_Click"/>
        public void ClipboardCopy_Click(object sender, RoutedEventArgs e) { /* TODO */ }      //Sondre

        // <MenuItem Header = "Paste"  Click="ClipboardPaste_Click"/>
        public void ClipboardPaste_Click(object sender, RoutedEventArgs e) { /* TODO */ }      //Sondre

        // <MenuItem Header = "Cut"    Click="ClipboardCut_Click"/>
        public void ClipboardCut_Click(object sender, RoutedEventArgs e) { /* TODO */ }      //Sondre
    }
}
