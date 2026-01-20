export default function Footer() {
  return (
    <footer className="bg-white border-t border-gray-200 mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="flex flex-col sm:flex-row justify-between items-center gap-4">
          <div className="text-sm text-gray-600">
            <p>&copy; {new Date().getFullYear()}  Clevion AI Chat Application. All rights reserved.</p>
          </div>
          <div className="flex items-center gap-6 text-sm text-gray-600">
            <a
              href="#"
              className="hover:text-blue-600 transition-colors"
              onClick={(e) => e.preventDefault()}
            >
              Privacy Policy
            </a>
            <a
              href="#"
              className="hover:text-blue-600 transition-colors"
              onClick={(e) => e.preventDefault()}
            >
              Terms of Service
            </a>
            <a
              href="#"
              className="hover:text-blue-600 transition-colors"
              onClick={(e) => e.preventDefault()}
            >
              Support
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
}
